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
