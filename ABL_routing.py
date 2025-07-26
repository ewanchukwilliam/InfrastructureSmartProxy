import os
from typing import TYPE_CHECKING, Dict, List, Optional, Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

if TYPE_CHECKING:
    from mypy_boto3_route53.client import Route53Client
    from mypy_boto3_route53domains.client import Route53DomainsClient


def get_route53_client() -> "Route53Client":
    """Initialize and return Route53 DNS client with proper error handling."""
    access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    
    if not access_key or not secret_key:
        raise ValueError(
            "AWS credentials not found. Set AWS_ACCESS_KEY_ID and "
            "AWS_SECRET_ACCESS_KEY environment variables."
        )
    
    return boto3.client(
        "route53",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )


def get_route53domains_client() -> "Route53DomainsClient":
    """Initialize and return Route53 Domains client for domain registration."""
    access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    
    if not access_key or not secret_key:
        raise ValueError(
            "AWS credentials not found. Set AWS_ACCESS_KEY_ID and "
            "AWS_SECRET_ACCESS_KEY environment variables."
        )
    
    return boto3.client(
        "route53domains",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )


def create_hosted_zone(domain_name: str) -> Optional[str]:
    """Create a hosted zone for a domain."""
    try:
        route53 = get_route53_client()
        response = route53.create_hosted_zone(
            Name=domain_name,
            CallerReference=f"{domain_name}-{int(__import__('time').time())}"
        )
        hosted_zone_id = response["HostedZone"]["Id"].split("/")[-1]
        print(f"Created hosted zone for {domain_name}: {hosted_zone_id}")
        return hosted_zone_id
    except (BotoCoreError, ClientError) as e:
        print(f"Error creating hosted zone: {e}")
        return None


def update_dns_record(
    hosted_zone_id: str,
    record_name: str,
    record_type: str,
    record_value: str,
    ttl: int = 300
) -> bool:
    """Update or create a DNS record in a hosted zone."""
    try:
        route53 = get_route53_client()
        
        change_batch = {
            "Changes": [
                {
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": record_name,
                        "Type": record_type,
                        "TTL": ttl,
                        "ResourceRecords": [{"Value": record_value}]
                    }
                }
            ]
        }
        
        response = route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch=change_batch
        )
        
        change_id = response["ChangeInfo"]["Id"]
        print(f"DNS record updated: {record_name} -> {record_value} (Change ID: {change_id})")
        return True
        
    except (BotoCoreError, ClientError) as e:
        print(f"Error updating DNS record: {e}")
        return False


def route_domain_to_ip(domain_name: str, ip_address: str, hosted_zone_id: Optional[str] = None) -> bool:
    """Route a domain to an IP address using A record."""
    try:
        if not hosted_zone_id:
            # Try to find existing hosted zone
            hosted_zone_id = get_hosted_zone_id(domain_name)
            if not hosted_zone_id:
                print(f"No hosted zone found for {domain_name}. Creating one...")
                hosted_zone_id = create_hosted_zone(domain_name)
                if not hosted_zone_id:
                    return False
        
        return update_dns_record(hosted_zone_id, domain_name, "A", ip_address)
        
    except Exception as e:
        print(f"Error routing domain to IP: {e}")
        return False


def route_domain_to_load_balancer(
    domain_name: str, 
    load_balancer_dns: str, 
    hosted_zone_id: Optional[str] = None
) -> bool:
    """Route a domain to a load balancer using CNAME record."""
    try:
        if not hosted_zone_id:
            hosted_zone_id = get_hosted_zone_id(domain_name)
            if not hosted_zone_id:
                print(f"No hosted zone found for {domain_name}. Creating one...")
                hosted_zone_id = create_hosted_zone(domain_name)
                if not hosted_zone_id:
                    return False
        
        return update_dns_record(hosted_zone_id, domain_name, "CNAME", load_balancer_dns)
        
    except Exception as e:
        print(f"Error routing domain to load balancer: {e}")
        return False


def get_hosted_zone_id(domain_name: str) -> Optional[str]:
    """Get the hosted zone ID for a domain."""
    try:
        route53 = get_route53_client()
        response = route53.list_hosted_zones()
        
        for zone in response["HostedZones"]:
            if zone["Name"].rstrip(".") == domain_name.rstrip("."):
                return zone["Id"].split("/")[-1]
        
        return None
        
    except (BotoCoreError, ClientError) as e:
        print(f"Error getting hosted zone ID: {e}")
        return None


def list_dns_records(hosted_zone_id: str) -> Optional[List[Dict[str, Any]]]:
    """List all DNS records in a hosted zone."""
    try:
        route53 = get_route53_client()
        response = route53.list_resource_record_sets(HostedZoneId=hosted_zone_id)
        
        records = []
        for record_set in response["ResourceRecordSets"]:
            records.append({
                "name": record_set["Name"],
                "type": record_set["Type"],
                "ttl": record_set.get("TTL", "N/A"),
                "values": [rr["Value"] for rr in record_set.get("ResourceRecords", [])]
            })
        
        return records
        
    except (BotoCoreError, ClientError) as e:
        print(f"Error listing DNS records: {e}")
        return None


def delete_dns_record(hosted_zone_id: str, record_name: str, record_type: str) -> bool:
    """Delete a specific DNS record."""
    try:
        route53 = get_route53_client()
        
        # First get the current record to delete
        response = route53.list_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            StartRecordName=record_name,
            StartRecordType=record_type,
            MaxItems="1"
        )
        
        if not response["ResourceRecordSets"]:
            print(f"Record {record_name} ({record_type}) not found")
            return False
        
        record_set = response["ResourceRecordSets"][0]
        
        change_batch = {
            "Changes": [
                {
                    "Action": "DELETE",
                    "ResourceRecordSet": record_set
                }
            ]
        }
        
        route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch=change_batch
        )
        
        print(f"Deleted DNS record: {record_name} ({record_type})")
        return True
        
    except (BotoCoreError, ClientError) as e:
        print(f"Error deleting DNS record: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    domain = "example.com"
    target_ip = "192.168.1.100"
    
    print("Route53 Domain Routing Examples:")
    print("1. Route domain to IP address")
    # route_domain_to_ip(domain, target_ip)
    
    print("2. List DNS records for a domain")
    # hosted_zone_id = get_hosted_zone_id(domain)
    # if hosted_zone_id:
    #     records = list_dns_records(hosted_zone_id)
    #     for record in records:
    #         print(f"  {record['name']} ({record['type']}) -> {record['values']}")
    
    print("3. Route subdomain to different IP")
    # route_domain_to_ip(f"api.{domain}", "192.168.1.101")
    
    print("Uncomment the lines above to test the functions")
