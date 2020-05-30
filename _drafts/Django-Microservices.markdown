# Django & DRF Microservices

## MicroServices
- Single Bounded Context
- UI and Services
- Independent
- Self-Contained
- Local Storage
- Share nothing

## Django Components
- middleware
- request & response pipeline
- Celery
- Redis
- PostgreSQL

## Middleware
- Keep middleware short non-blocking
- conditional GET middleware
- GzipMiddleware
- Cached Sessions

## ORM
Maps objects to Database tables
- Add Indexes
- Enable persistent connections to database
- Use DB connection pooling
- prefect_related() M2M and M2One
- select_related() One2One single valued relationships
- Reuse QuerySets

Measurement Profiling
- django-debug-toolbar

## Caching
- when all else fails
- Read heavy workloads
- View level or custom level caching
- Invalidation can be complex

## Asynchronous Processing
- Deferred tasks
- Celery Queues


# Tips for Failing at Microservices
- make a polyglot a zoo of technology different languages,tech stacks
