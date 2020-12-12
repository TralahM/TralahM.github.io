RPS requests per second throughput

micro-prefix

## Benefits

- A microservice is a lightweight app with narrowed list of features
- one piece of a puzzle
- Does one thing well (single responsibility)
- Separation of concerns
- build, test, deploy, and ship faster

## Risks

 - Bad design decisions
 - Network Overhead Round trip
 - Testing is harder
 - Data storage and sharing is more complex
 - Compatibility issues

## Principles
- Microservices should happen on time not on day 1
- Premature splitting is the root of all evil
- Dont design CRUD microservices

## Standard Protocols
- Json| Http1.0
- REST
- msgpack
- RPC
- Swagger, Json Schema
- Token Based Authentication (OAuth2,JWT-Tokens)

## Designing HTTP API
- Version your API (Backward Compatibility)
- Dont CRUD too much
- Use JSON Schemas

## Frameworks
- Flask
- Bottle
- Connexion
- Aiohttp
- Falcon
- Twisted
- Tornado
