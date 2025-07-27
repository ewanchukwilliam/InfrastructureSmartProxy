import os
from typing import TYPE_CHECKING, Dict, List, Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from mypy_boto3_ec2.client import EC2Client
from mypy_boto3_ec2.type_defs import StartInstancesResultTypeDef, StopInstancesResultTypeDef, TerminateInstancesResultTypeDef

from accounts.models import User


def get_ec2_client(user: User) -> EC2Client:
    """Initialize and return EC2 client with proper error handling."""
    access_key = user.access_key_id
    secret_key = user.secret_access_key 
    secret_key = user.secret_access_key
    region = "us-east-1"
    
    if not access_key or not secret_key:
        raise ValueError(
            "AWS credentials not found. Set AWS_ACCESS_KEY_ID and "  # pyright: ignore[reportImplicitStringConcatenation]
            "AWS_SECRET_ACCESS_KEY environment variables."
        )
    client: EC2Client = boto3.client(
        service_name="ec2",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    return client
    

def start_ec2_instances(instance_ids: list[str]) -> StartInstancesResultTypeDef | None:
    """Start EC2 instances."""
    try:
        ec2 = get_ec2_client()
        response = ec2.start_instances(InstanceIds=instance_ids)
        print(f"Starting instances: {instance_ids}")
        return response
    except (BotoCoreError, ClientError) as e:
        print(f"Error starting instances: {e}")
        return None

def stop_ec2_instances(instance_ids: list[str]) -> StopInstancesResultTypeDef | None:
    """Stop EC2 instances."""
    try:
        ec2 = get_ec2_client()
        response = ec2.stop_instances(InstanceIds=instance_ids)
        print(f"Stopping instances: {instance_ids}")
        return response
    except (BotoCoreError, ClientError) as e:
        print(f"Error stopping instances: {e}")
        return None

def terminate_ec2_instances(instance_ids: list[str]) -> TerminateInstancesResultTypeDef | None:
    """Terminate (delete) EC2 instances."""
    try:
        ec2 = get_ec2_client()
        response = ec2.terminate_instances(InstanceIds=instance_ids)
        print(f"Terminating instances: {instance_ids}")
        return response
    except (BotoCoreError, ClientError) as e:
        print(f"Error terminating instances: {e}")
        return None

def create_ec2_instance(
    ami_id: str, 
    instance_type: str = "t2.micro", 
    key_name: str | None = None, 
    security_group_ids: list[str] | None = None, 
    subnet_id: str | None = None
) -> str | None:
    """Create a new EC2 instance."""
    try:
        ec2 = get_ec2_client()
        
        # Build parameters for run_instances
        params: dict[str, object] = {
            "ImageId": ami_id,
            "InstanceType": instance_type,
            "MinCount": 1,
            "MaxCount": 1
        }

        if key_name:
            params["KeyName"] = key_name
        if security_group_ids:
            params["SecurityGroupIds"] = security_group_ids
        if subnet_id:
            params["SubnetId"] = subnet_id

        response = ec2.run_instances(**params)
        instance_id = response["Instances"][0].get("InstanceId")
        print(f"Created instance: {instance_id}")
        return instance_id
    except (BotoCoreError, ClientError) as e:
        print(f"Error creating instance: {e}")
        return None


