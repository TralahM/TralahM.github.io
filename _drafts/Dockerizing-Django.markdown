## What is Docker
System for containerizing your apps/software
Like a VM but not quite
- no Hypervisor
- uses Linux kernel features to isolate environments while sharing the same OS
- Faster Startup as there's less overhead

## Why Docker
- Eliminate it doesn't work on my machine
- 12 Factor app
    + Dev/Production Parity almost similar
    + Store config in the environment
    + And more
- deployment alternatives ECS, Kubernetes,Heroku

## How to use Docker
Create a ./Dockerfile
```Dockerfile
FROM python:3.7
COPY requirements.txt
RUN pip install -r requirements.txt
COPY . /app
CMD python manage.py
```

Create a ./dockercompose.yml
```yaml
version: '2'
services:
    web:
        build: .
        ports:
            - "8000:8000"
        volumes:
            - .:/app
        links:
            - db
db:
    image: "postgres:9.6"
    ports:
        - "5432:5432"
    environment:
        POSTGRES_PASSWORD: hunter2
```

## Making a Production-ready container
- Don't use django development server in a production setting
- Nginx, gunicorn
 Nginx to serve static files and proxy django
 Load balancing, Unix Socket
