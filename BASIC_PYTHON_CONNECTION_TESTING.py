import boto3
import time
import logging
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# AWS configuration (modify these as needed)
REGION = 'us-east-1'
AMI_ID = 'ami-0c55b159cbfafe1f0'  # Example: Amazon Linux 2 AMI (update for your region)
INSTANCE_TYPE = 't2.micro'
KEY_NAME = 'my-key-pair'  # Replace with your EC2 key pair name
SECURITY_GROUP_IDS = ['sg-1234567890abcdef0']  # Replace with your security group ID

def create_ec2_instance(ec2_client, ami_id=AMI_ID, instance_type=INSTANCE_TYPE, key_name=KEY_NAME, security_group_ids=SECURITY_GROUP_IDS):
    """Launch a new EC2 instance."""
    try:
        response = ec2_client.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=key_name,
            SecurityGroupIds=security_group_ids,
            MinCount=1,
            MaxCount=1
        )
        instance_id = response['Instances'][0]['InstanceId']
        logger.info(f"Launched EC2 instance: {instance_id}")
        
        # Wait for the instance to be running
        waiter = ec2_client.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
        logger.info(f"Instance {instance_id} is now running")
        return instance_id
    except ClientError as e:
        logger.error(f"Failed to launch instance: {e}")
        raise

def start_ec2_instance(ec2_client, instance_id):
    """Start an existing EC2 instance."""
    try:
        response = ec2_client.start_instances(InstanceIds=[instance_id])
        logger.info(f"Starting EC2 instance: {instance_id}")
        
        # Wait for the instance to be running
        waiter = ec2_client.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
        logger.info(f"Instance {instance_id} started successfully")
    except ClientError as e:
        logger.error(f"Failed to start instance {instance_id}: {e}")
        raise

def stop_ec2_instance(ec2_client, instance_id):
    """Stop an existing EC2 instance."""
    try:
        response = ec2_client.stop_instances(InstanceIds=[instance_id])
        logger.info(f"Stopping EC2 instance: {instance_id}")
        
        # Wait for the instance to be stopped
        waiter = ec2_client.get_waiter('instance_stopped')
        waiter.wait(InstanceIds=[instance_id])
        logger.info(f"Instance {instance_id} stopped successfully")
    except ClientError as e:
        logger.error(f"Failed to stop instance {instance_id}: {e}")
        raise

def main():
    """Main function to demonstrate EC2 instance management."""
    try:
        # Initialize EC2 client
        ec2_client = boto3.client('ec2', region_name=REGION)
        
        # Launch a new instance
        instance_id = create_ec2_instance(ec2_client)
        
        # Wait for a few seconds to ensure instance is fully initialized
        time.sleep(10)
        
        # Stop the instance
        stop_ec2_instance(ec2_client, instance_id)
        
        # Wait for a few seconds to ensure instance is stopped
        time.sleep(10)
        
        # Start the instance again
        start_ec2_instance(ec2_client, instance_id)
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
