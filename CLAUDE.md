# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

InfrastructureSmartProxy is a Django-based backend service for running Infrastructure as Code (Terraform) on a locally hosted server. The project is considering migration from Terraform to boto3 for AWS resource management.

## Architecture

This is a Django 5.2.4 project with the following structure:
- **InfraSmartRouter/**: Main Django project directory containing settings, URLs, WSGI/ASGI configuration
- **manage.py**: Standard Django management script
- **Docker containerization**: Full Docker Compose setup with PostgreSQL (pgvector), Redis, and Nginx
- **Database**: PostgreSQL with pgvector extension for vector operations
- **Caching**: Redis for session management and caching

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Docker Development
```bash
# Start all services
docker-compose up

# Start with Jupyter notebook
docker-compose --profile jupyter up

# Rebuild and start
docker-compose up --build

# View logs
docker-compose logs [service_name]
```

### Database Management
The project uses PostgreSQL with pgvector extension. Database configuration is handled through environment variables in docker-compose.yml:
- DB_NAME: postgres
- DB_HOST: db 
- DB_USER: postgres
- DB_PASSWORD: postgres
- DB_PORT: 5432

## Environment Configuration

The project uses Docker Compose environment variables:
- **STAGE**: "DEV" for development
- **DEBUG**: "True" for development mode
- **PYTHONUNBUFFERED**: 1 for proper logging in containers
- **REDIS_AUTH**: testing123
- **REDIS_HOST**: redis
- **REDIS_PORT**: 6379

## Services Architecture

- **CentralRouter**: Main Django application (port 8000)
- **Database**: PostgreSQL with pgvector (port 5432)
- **Redis**: Cache and session store (port 6379)
- **Nginx**: Reverse proxy (port 80)
- **Jupyter** (optional): Development notebook environment (port 8888)

## Important Notes

- The project is in early development with basic Django setup
- Settings contain placeholder database credentials that need environment variable override
- Docker volume mapping includes `/var/run/docker.sock` for Docker-in-Docker operations
- No custom Django apps are currently implemented - only the base project structure exists