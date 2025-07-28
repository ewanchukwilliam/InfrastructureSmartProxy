
import json
from typing import Any
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from resources.models import EC2Instance

User = get_user_model()

def get_default_user():
    """Get the default superuser for operations"""
    return User.objects.filter(is_superuser=True).first()


def index(request: HttpRequest)-> HttpResponse:
    instances = EC2Instance.objects.all()
    context = {
        'instances': instances,
    }
    return render(request, "index.html", context)    

@require_POST
def start_instance(request: HttpRequest, instance_id: str)-> HttpResponse:
    instance = get_object_or_404(EC2Instance, id=instance_id)
    success = instance.start_instance()
    return JsonResponse({
        'success': success,
        'status': instance.status,
        'message': f"Instance {'started' if success else 'failed to start'}"
    })

@require_POST
def stop_instance(request: HttpRequest, instance_id: str)-> HttpResponse:
    instance = get_object_or_404(EC2Instance, id=instance_id)
    success = instance.stop_instance()
    return JsonResponse({
        'success': success,
        'status': instance.status,
        'message': f"Instance {'stopped' if success else 'failed to stop'}"
    })

@require_POST
def terminate_instance(request: HttpRequest, instance_id: str)-> HttpResponse:
    instance = get_object_or_404(EC2Instance, id=instance_id)
    success = instance.terminate_instance()
    return JsonResponse({
        'success': success,
        'status': instance.status,
        'message': f"Instance {'terminated' if success else 'failed to terminate'}"
    })

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

@require_POST
def create_instance(request: HttpRequest)-> HttpResponse:
    
    try:
        data: object = json.loads(request.body)
        
        # Get the default superuser
        default_user = get_default_user()
        if not default_user:
            return JsonResponse({
                'success': False,
                'message': 'No default user found. Please run migrations.'
            })
        
        # Create new EC2Instance with defaults and user input
        instance = EC2Instance.objects.create(
            name=data.get('name', f'instance-{default_user.username}-{len(EC2Instance.objects.filter(creating_user=default_user)) + 1}'),
            creating_user=default_user,
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


# these lines exist because neovim 11.3 is breaking when you delete the eof line
# these lines exist because neovim 11.3 is breaking when you delete the eof line
# these lines exist because neovim 11.3 is breaking when you delete the eof line
# these lines exist because neovim 11.3 is breaking when you delete the eof line
# these lines exist because neovim 11.3 is breaking when you delete the eof line
# these lines exist because neovim 11.3 is breaking when you delete the eof line
