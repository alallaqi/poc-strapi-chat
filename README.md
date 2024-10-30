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

---

Base flow:

```mermaid
flowchart
   
   Input[/user input/] --> preprocess[Preprocess the input<br /> to extract parameters required in the APIs]
   preprocess --> A
   A[create the design] --> B[Link design to site config]
   B --> C[Create a content page]


```

---

1. Create the design  
   API: designs (POST)
   - design name
   - primary color
   - secondary color
   - fonts

2. Link design to site config
   API: site-config
   - design

3. Create a basic content page
   API: content-pages (POST)

4.


## Getting started

Install dependencies:

```bash
pip install -r requirements.txt
```

