# InfrastructureSmartProxy

## Description

this is a smart django backend for running infrastructure as code (terraform) on a locally hosted server.

## Requirements

- python 3.8+
- django 3.1+
- terraform 0.12+

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Run the server

```bash
python manage.py runserver
```

### Run the server with gunicorn

```bash
gunicorn infrastructure_smart_proxy.wsgi:application
```

# in case I forget how to create a new superuser
python manage.py createsuperuser --email admin@example.com --username admin

# TODO: 
 
- [ ] test credentials and crud operations for user/ec2instance table
- [ ] create views for site visitors to interact with the containers
- [ ] create a redis scheduled task to stop and terminate containers


# MIGHT BE ABLE TO USE boto3 to do this instead of terraform
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances
