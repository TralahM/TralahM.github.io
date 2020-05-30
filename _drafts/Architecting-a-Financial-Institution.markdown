# Core Banking + Credit Card Architecture
Functional Architecture
Event Sourcing

Subscriber/Consumer
Publisher

- Authorizer
- Realtime Transfers
    Scan QR code and money is transferred
- General Ledgers
 Maintaining idempotence
- KYC
- Credit Scoring

## Purchase Authorization Value Chain
Multiplexing Network Connections
Issuer Authorization: Requirements
- Highly available
- Building on Physical Infrastructure (Bare Metal)

## Inter-Service Communication
- Kafka
 + Kafka Topic Partition
 + Kafka Based Log/Snapshot
 + Authorizer Consumer
 + AWS service Publisher

Business Logic depends on data across many services

## Scaling Plan
Need to partition the workload
1. Partition Service Databases
    + Database writes are the worst  bottlenecks
    + Maybe horizontally partition each database
    + Change every service to route queries and writes to the appropriate shard

    Issues:
    + Enormous effort to change every service
    + Risk intermingling data infrastructure code with business logic
    + Doesn't address non-db bottlenecks

2. Scalability Units + Global Routing
    Global Services to map external identifiers to internal shards,partitions
    - Automated Immutable Infrastructure
    - Messaging and Hypermedia
    - Splitting Existing Data

3. Fault Tolerance Patterns
- Circuit breakers
- Dead letters

Sharding and Partitions makes analysis harder

## ETL + The Analytical Environment

Extract, transform, and load
Datomic and Kafka Log extraction feed the data lake in real-time
Decoupling and asynchronous messaging
