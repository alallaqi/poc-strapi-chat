# Chat with your middleware

A simple Proof of Concept (PoC) demonstrating how ChatGPT can serve as an interface to RESTful (OpenAPI) middleware systems.

## Abstract

Middleware in enterprise IT architectures is crucial, acting as the connective tissue between different internal and external systems, applications, storage solutions, and databases. It provides operational support, enabling the implementation of cross-domain business processes. This layer encompasses a range of services, APIs, queue systems, and more, facilitating seamless interactions across diverse IT environments.

Middleware can adopt various architectural patterns, such as Service-Oriented Architecture (SOA), microservices, or Enterprise Service Bus (ESB), sometimes integrating multiple approaches. It supports various message formats (e.g., SOAP, REST, gRPC, files) and operates over assorted technologies and protocols (e.g., web services, queuing and log systems, email, FTP). Primarily, middleware focuses on connectivity and reliability—often ensured by queuing or log systems like Kafka—without storing data itself.

As enterprises evolve, middleware platforms rapidly expand, incorporating an ever-increasing number of services and processes. This growth, while indicative of scalability, often leads to challenges in service identification and reuse. Moreover, the fragmentation and potential obsolescence of documentation, combined with knowledge silos, complicate the efficient leverage of existing capabilities.

This landscape complicates the introduction of new business processes, making it challenging to identify and utilize pre-existing services and workflows. This PoC introduces an innovative solution: interacting with middleware through conversational AI. This approach leverages technical documentation, such as OpenAPI definitions, and ChatGPT to:

1. Suggest relevant services for specific tasks.
2. Automate the execution of requests to these services to implement business flows.

This method not only streamlines the identification and utilization of middleware services but also enhances documentation accessibility and fosters a more dynamic, user-friendly approach to middleware interaction.

## Dependencies

openai
pyyaml
