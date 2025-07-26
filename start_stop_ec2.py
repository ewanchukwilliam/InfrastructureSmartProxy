import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError

AMI_ID = "ami-08a6efd148b1f7504"
def get_ec2_client():
    """Initialize and return EC2 client with proper error handling"""
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    ami_id = os.environ.get('AMI_ID')
    
    if not access_key or not secret_key:
        raise ValueError("AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
    
    return boto3.client(
        'ec2',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

def start_ec2_instances(instance_ids):
    """Start EC2 instances"""
    try:
        ec2 = get_ec2_client()
        response = ec2.start_instances(InstanceIds=instance_ids)
        print(f"Starting instances: {instance_ids}")
        return response
    except (BotoCoreError, ClientError) as e:
        print(f"Error starting instances: {e}")
        return None

def stop_ec2_instances(instance_ids):
    """Stop EC2 instances"""
    try:
        ec2 = get_ec2_client()
        response = ec2.stop_instances(InstanceIds=instance_ids)
        print(f"Stopping instances: {instance_ids}")
        return response
    except (BotoCoreError, ClientError) as e:
        print(f"Error stopping instances: {e}")
        return None

def create_ec2_instance(ami_id, instance_type='t2.micro', key_name=None, security_group_ids=None, subnet_id=None):
    """Create a new EC2 instance"""
    try:
        ec2 = get_ec2_client()
        
        # Build parameters for run_instances
        params = {
            'ImageId': ami_id,
            'InstanceType': instance_type,
            'MinCount': 1,
            'MaxCount': 1
        }
        
        if key_name:
            params['KeyName'] = key_name
        if security_group_ids:
            params['SecurityGroupIds'] = security_group_ids
        if subnet_id:
            params['SubnetId'] = subnet_id
            
        response = ec2.run_instances(**params)
        instance_id = response['Instances'][0].get('InstanceId')
        print(f"Created instance: {instance_id}")
        return instance_id
    except (BotoCoreError, ClientError) as e:
        print(f"Error creating instance: {e}")
        return None

if __name__ == "__main__":
    # Replace with your actual instance IDs
    INSTANCE_IDS = ['i-0123456789abcdef0']
    

    create_ec2_instance(AMI_ID)
    # Uncomment the operation you want to perform
    # start_ec2_instances(INSTANCE_IDS)
    # stop_ec2_instances(INSTANCE_IDS)
