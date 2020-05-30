- Domain Driven Design
- Event Driven Systems
- Distributed Systems

- Event->Stream->EventStore

- Projection->Aggregation-> Read Models
handlers, by time, metrics, database postgres

Design as much as possible around shared-nothing
Encapsulate state
Signed cookie sessions
On demand thumbnailing

- HTTP proxy balancer
- Cache per instance
- Scaling Databases

# CAP Theorem

## Partition Tolerant
- Over network connections

## Available

## Consistent
- Read Replications
- Sharding (vertical and horizontal)
- Vertical sharding
- Horizontal sharding

Managing program complexity

# Services
splitting data from the business logic
each service is its own small project managed and scaled separately
how do you communicate between them??
- Direct http communication
 increases quadratically as services increase
- Routed Http connections (Router)
- Message Bus with queueing and routing
 Introduces a single point of failure though
 Easy to monitor and understand
 Not bad if multiple services are fragile

# Django Channels
Channels and ASGI provide a standard message bus but with certain trade-offs

## Guarantees vs Latency
- Low latency
- Low loss rate

## Queueing Type
- FIFO consistent performance for all users
- LIFO hides backlogs but makes them worse

## Queue Sizing
- Finite Queues
- Infinite Queues

## Failure Mode
- At most Once
- At Least Once
