
from typing import Callable
import boto3
import json
from functools import wraps
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from resources.models import EC2Instance

User = get_user_model()

def get_default_user():
    """Get the default superuser for operations"""
    return User.objects.filter(is_superuser=True).first()

def ensure_user_available(view_func: Callable):
    """
    Decorator that ensures a user is available for operations.
    Uses authenticated user if available, otherwise falls back to default superuser.
    Returns 400 JSON response if no user is available.
    """
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        user = request.user if request.user.is_authenticated else get_default_user()
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'No user available for operation'
            }, status=400)
        
        # Add user to request so view functions can access it
        request.operation_user = user
        return view_func(request, *args, **kwargs)
    return wrapper


@require_http_methods(["GET"])
def index(request: HttpRequest)-> HttpResponse:
    instances = EC2Instance.objects.all()
    context = {
        'instances': instances,
    }
    return render(request, "index.html", context)    

@require_http_methods(["POST"])
def start_instance(request: HttpRequest, instance_id: str)-> HttpResponse:
    instance = get_object_or_404(EC2Instance, id=instance_id)
    success = instance.start_instance()
    return JsonResponse({
        'success': success,
        'status': instance.status,
        'message': f"Instance {'started' if success else 'failed to start'}"
    })

@require_http_methods(["POST"])
def stop_instance(request: HttpRequest, instance_id: str)-> HttpResponse:
    instance = get_object_or_404(EC2Instance, id=instance_id)
    success = instance.stop_instance()
    return JsonResponse({
        'success': success,
        'status': instance.status,
        'message': f"Instance {'stopped' if success else 'failed to stop'}"
    })

@require_http_methods(["POST"])
def terminate_instance(request: HttpRequest, instance_id: str)-> HttpResponse:
    instance = get_object_or_404(EC2Instance, id=instance_id)
    success = instance.terminate_instance()
    return JsonResponse({
        'success': success,
        'status': instance.status,
        'message': f"Instance {'terminated' if success else 'failed to terminate'}"
    })

@require_http_methods(["GET"])
def check_instance_status(request: HttpRequest, instance_id: str)-> HttpResponse:
    instance = get_object_or_404(EC2Instance, id=instance_id)
    current_status = instance.get_instance_status()
    current_ip = instance.get_instance_ip_address()
    
    return JsonResponse({
        'status': current_status or instance.status,
        'ip_address': current_ip or instance.ip_address,
        'name': instance.name,
        'instance_type': instance.instance_type,
        'region': instance.region
    })

@ensure_user_available
@require_http_methods(["POST"])
def create_instance(request: HttpRequest)-> HttpResponse:
    
    try:
        data: object = json.loads(request.body)
        
        # Get user from decorator
        user = request.operation_user
        
        # Create new EC2Instance with defaults and user input
        instance = EC2Instance.objects.create(
            name=data.get('name', f'instance-{user.username}-{len(EC2Instance.objects.filter(creating_user=user)) + 1}'),
            creating_user=user,
            username=data.get('username', 'ubuntu'),  # Default Ubuntu username
            password=data.get('password', ''),  # Usually empty for key-based auth
            instance_type=data.get('instance_type', 't2.micro'),  # Default from model
            region=data.get('region', 'us-east-1'),  # Default from model
            status='pending'  # Start with pending status
        )
        
        # Create the actual AWS instance
        aws_instance_id = instance.create_instance()
        
        if aws_instance_id:
            return JsonResponse({
                'success': True,
                'message': f'Instance {instance.name} created successfully',
                'instance_id': instance.id,
                'aws_instance_id': aws_instance_id
            })
        else:
            # If AWS creation failed, delete the database record
            instance.delete()
            return JsonResponse({
                'success': False,
                'message': 'Failed to create AWS instance'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating instance: {str(e)}'
        })

@ensure_user_available
def sync_aws_instances(request: HttpRequest):
    """Sync AWS instances with database (internal function)"""
    
    try:
        # Get user from decorator
        user = request.operation_user
            
        # Iterate through all regions
        for region_code, region_name in EC2Instance.REGION_CHOICES:
            try:
                # Get AWS instances for this region
                ec2_client = boto3.client('ec2', region_name=region_code)
                boto3_instances = ec2_client.describe_instances()
                
                for reservation in boto3_instances['Reservations']:
                    for instance in reservation['Instances']:
                        # Extract AWS data
                        aws_instance_id = instance['InstanceId']
                        state = instance['State']['Name']
                        instance_type = instance['InstanceType']
                        public_ip = instance.get('PublicIpAddress')
                        region = instance['Placement']['AvailabilityZone'][:-1]
                        
                        # Get instance name from tags
                        name = aws_instance_id
                        for tag in instance.get('Tags', []):
                            if tag['Key'] == 'Name':
                                name = tag['Value']
                                break
                        
                        # Update or create database record
                        EC2Instance.objects.update_or_create(
                            aws_instance_id=aws_instance_id,
                            defaults={
                                'name': name,
                                'status': state,
                                'instance_type': instance_type,
                                'ip_address': public_ip,
                                'region': region,
                                'creating_user': user,
                                'username': 'ubuntu',
                            }
                        )
            except Exception as e:
                print(f"Error syncing instances from region {region_code}: {e}")
                continue
        print(f"Synced {len(EC2Instance.objects.all())} instances")
    except Exception as e:
        print(f"Error syncing AWS instances: {e}")

@ensure_user_available
@require_http_methods(["POST"])
def get_instances(request: HttpRequest) -> HttpResponse:
    """API endpoint to sync and return instances"""
    
    try:
        # Get user from decorator
        user = request.operation_user
            
        synced_instances = []
        
        # Iterate through all regions
        for region_code, region_name in EC2Instance.REGION_CHOICES:
            try:
                # Get AWS instances for this region
                ec2_client = boto3.client('ec2', region_name=region_code)
                boto3_instances = ec2_client.describe_instances()
                
                for reservation in boto3_instances['Reservations']:
                    for instance in reservation['Instances']:
                        # Extract AWS data
                        aws_instance_id = instance['InstanceId']
                        state = instance['State']['Name']
                        instance_type = instance['InstanceType']
                        public_ip = instance.get('PublicIpAddress')
                        region = instance['Placement']['AvailabilityZone'][:-1]
                        
                        # Get instance name from tags
                        name = aws_instance_id
                        for tag in instance.get('Tags', []):
                            if tag['Key'] == 'Name':
                                name = tag['Value']
                                break
                        
                        # Update or create database record
                        db_instance, created = EC2Instance.objects.update_or_create(
                            aws_instance_id=aws_instance_id,
                            defaults={
                                'name': name,
                                'status': state,
                                'instance_type': instance_type,
                                'ip_address': public_ip,
                                'region': region,
                                'creating_user': user,
                                'username': 'ubuntu',
                            }
                        )
                        
                        synced_instances.append({
                            'id': db_instance.id,
                            'aws_instance_id': aws_instance_id,
                            'name': name,
                            'state': state,
                            'type': instance_type,
                            'ip_address': public_ip,
                            'region': region,
                            'created': created
                        })
            except Exception as e:
                print(f"Error syncing instances from region {region_code}: {e}")
                continue
        
        return JsonResponse({
            'success': True,
            'synced_count': len(synced_instances),
            'instances': synced_instances
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


    


# these lines exist because neovim 11.3 is breaking when you delete the eof line
# these lines exist because neovim 11.3 is breaking when you delete the eof line
# these lines exist because neovim 11.3 is breaking when you delete the eof line
# these lines exist because neovim 11.3 is breaking when you delete the eof line
# these lines exist because neovim 11.3 is breaking when you delete the eof line
# these lines exist because neovim 11.3 is breaking when you delete the eof line
