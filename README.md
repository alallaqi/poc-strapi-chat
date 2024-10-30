# Strapi Chat

Automate Stripe site creation with LangChain + OpenAPI + LLM.

See [OpenAPI | 🦜️🔗 Langchain](https://python.langchain.com/docs/integrations/toolkits/openapi) for more details on usinig LLMs to interact with OpenAPI APIs.

## Atchitecture

High level architecture of the app.

```mermaid
graph LR
    subgraph StrapiChat
      P[/Prompt/] --> LC[Lang Chain]
      AD[/APIs definition/] --> |RAG|LC
      LC -.-> LLM[LLM] -.-> LC
    end
    LC -.-> |calls|SA[Strapi APIs]
```

Sequence diagram 

```mermaid
sequenceDiagram
    User->>StrapiChat: Build site bla bla bla
    StrapiChat->>LangChain: Prompt + API Definition
    LangChain->>LLM: What APIs should be used?
    LLM->>LangChain: API x, y, z with params a, b, c.
    LangChain->>Strapi APIs: Call API x with param a
    Strapi APIs->>LangChain: Response API x
    Note over LangChain,Strapi APIs: Interaction continues eventually <br /> also mapping and adjusting the inpur
    LangChain->>StrapiChat: Agent Logs
    StrapiChat->>User: Final feedback
```

## Getting started

Install dependencies:

```bash
pip install -r requirements.txt
```