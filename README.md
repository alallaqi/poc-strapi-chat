# Strapi Chat

Automate creation of Strapi web sites with a reasoning and action (ReAct) AI agent using LangGraph, LLM (OpenAI) and custom tools to interact with strapi APIs.

## Context

### Strapi

**Strapi** is an open-source, headless CMS (Content Management System) designed to help developers manage and deliver content via APIs. It offers a customizable backend with support for dynamic content modeling, making it ideal for building flexible and scalable content-driven applications.

### Application Programming Interfaces (APIs)

**APIs** are intermediaries that allow different software applications to communicate with each other. They define rules and protocols for accessing functionality or data, enabling seamless integration between systems, such as retrieving data from a CMS like Strapi or connecting to third-party services.

### Large Language Model (LLM)

**LLM** refers to advanced AI models trained on vast amounts of text data to understand and generate human-like language. These models, such as GPT or T5, leverage billions of parameters to perform tasks like text generation, translation, summarization, and question answering. Their versatility makes them a cornerstone for modern AI applications.

### Retrieval-Augmented Generation (RAG)

Retrieval-Augmented Generation (RAG) is an approach in artificial intelligence that combines a retrieval system with a generative model to generate more accurate, contextually relevant, and knowledge-grounded responses. It is commonly used in applications like question answering, content generation, and conversational AI.

### LangChain, LangGraph, and Agents

**LangChain** is a framework designed to build advanced applications powered by large language models (LLMs). It enables seamless integration of language models with tools, external data, and workflows, making it easier to create context-aware, interactive, and robust AI-driven systems.

**LangGraph** extends LangChain by introducing graph-based workflows, where nodes represent logical steps (e.g., data retrieval, decisions, or tool actions) and edges define the flow of information. This enables modular and transparent AI application development with complex reasoning paths.

**Agents** in LangChain/LangGraph are dynamic systems that use LLMs to decide which actions to take, such as calling tools, querying data sources, or performing computations. They follow structured reasoning steps (e.g., ReAct) to handle user inputs interactively and adaptively.

## Atchitecture

### ❌ Option 1 - OpenAPI Agent

> ⚠️ **PROPOSAL REJECTED** - See the "Decision" section for more details.

```mermaid
graph TD
    WU[Web UI] --> P
    CA[Console App] --> P
    subgraph StrapiChat
      P[/Prompt/] --> LC["OpenAPI Agent"]
      AD[/APIs definition/] --> LC
      LC -.-> LLM[LLM] -.-> LC
    end
    LC -.-> |calls|SA[Strapi APIs]
```

In the diagam above are illustrated the components and the connections of the "Open API Agent" solution. Dashed lines represent fulli automated links of which we have no control. Solid lines represent links in which we cann fully or partially influence.

Using LangChain's OpenAPI agent, we can automate API calls. By crafting the right prompt,
we can guide the agent to execute a specific sequence of calls, detailing the input parameters
for each request and the information to extract from the responses.

The diagram below illustrates a sample RAG flow using the LangChain OpenAPI agent to interact with Strapi APIs.

```mermaid
sequenceDiagram
    User->>StrapiChat: Build site bla bla bla
    StrapiChat->>OpenAPI Agent: Prompt + API Definition
    OpenAPI Agent->>LLM: What APIs should be used?
    LLM->>OpenAPI Agent: API x, y, z with params a, b, c.
    OpenAPI Agent->>Strapi APIs: Call API x with param a
    Strapi APIs->>OpenAPI Agent: Response API x
    Note over OpenAPI Agent,Strapi APIs: Interaction continues eventually <br /> also mapping and adjusting the input
    OpenAPI Agent->>StrapiChat: Agent Logs
    StrapiChat->>User: Final feedback
```

### ✅ Option 2 - Custom Strapi Agent with LangGraph

```mermaid
graph TD
    WU[Web UI] --> P
    CA[Console App] --> P
    subgraph StrapiChat
      P[/Prompt/] --> LC["Custom Strapi Agent"]
      LC --> CT[Custom Tools]
      LC --> LLM[LLM] -.-> LC
    end
    CT --> |calls|SA[Strapi APIs]
```

In the diagam above are illustrated the components and the connections of the "Custom Strapi Agent" solution. Dashed lines represent fulli automated links of which we have no control. Solid lines represent links in which we cann fully or partially influence.

In this solution, we build a custo agent that has a defined set of pre-coded toolsto interact with the Strapi APIs. The role of the LLM is then to decide which tools to use and what parameters pass in input. To achieve this goal we adopt a ReAct (reasoning and action) approach for our agent. The agent first creates a plan of which tools to use, with a defined sequence, then execute the tool, which connects with the Strapi APIs, and eveluates if to update the plan based on the result of the tool (observation).

### Decison

Based on the table below, the solution selected is: **Option 2: Custom Strapi Agent with LangGraph**

| Feature/Aspect                  | Option 1: OpenAPI Agent                                                                 | Option 2: Custom Strapi Agent with LangGraph                                      |
|---------------------------------|----------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **🛠️ Use Case Suitability**        | ❌ Suitable for simple API interactions                                                | ✅ Ideal for complex, multi-step interactions requiring custom logic               |
| **📈 Result Consistency**        | ❌ Low, frequent errors in calling APIs or parsing results                              | ✅ High, even with complex workflows                                               |
| **🧩 Implementation Complexity**   | ❌ Lower code complexity but increased prompt complexity                               | ✅ Relatively low code complexity and very low prompt complexity                   |
| **⚠️ Error Handling**              | ❌ Relies on the OpenAPI agent's built-in error handling mechanisms                     | ✅ Customizable error handling tailored to specific needs                          |
| **🚀 Performance**                 | ❌ Frequent errors significantly impact performance                                     | ✅ Can be optimized for specific use cases and performance requirements            |
| **💰 Token Usage**        | ❌ Higher due to API definitions and frequent agent adjustments                        | ✅ Lower as no API definition is loaded and minimal agent adjustments           |

## Implementation of the Custom LangGraph Agent

### Agent Architecture

The Strapi agent, follws a common reasoning and action (ReAct) architecture with additional initial steps required to consisently handle the first user input validation. The  customized agent is built using LangGraph and also paired with a basic Web UI exposed via Flask. The agent is provided with a set of "tools" (functions) which represent basic operations on the Strapi APIs, such as for example adding an image, or creating a page. The tools allows for a customize handling of the Strapi APIs reducing the errors, the token usage and allowing for more precise, consistent and granular interaction with the APIs.

In a normal interaction, the user provides a company profile description and the the agent:

1. Checks if the text in input is good enough and extracts some basic details to set up the design and upload a few AI generated demo images.
2. Uses a preset prompt to create the default web site structure.
3. ✨ Allows for further interactions after the initial creation.  E.g.  the user can tell the agent to add a text or an image into a specific page.

```mermaid
%%{init: {'flowchart': {'curve': 'linear'}}}%%
graph TD;
        __start__([<p>__start__</p>]):::first
        generate_site_data(generate_site_data)
        input_company_profile(input_company_profile)
        planner(planner)
        agent(agent)
        replan(replan)
        __end__([<p>__end__</p>]):::last
        agent --> replan;
        input_company_profile --> generate_site_data;
        planner --> agent;
        __start__ -.-> input_company_profile;
        __start__ -.-> planner;
        generate_site_data -.-> input_company_profile;
        generate_site_data -.-> planner;
        replan -.-> agent;
        replan -.-> __end__;
```



### Tools

- [x] Set up design (including a few AI generated demo images)
- [ ] Navigation
- [x] Create page
- [x] Add text component
- [x] Add image component (using existing image)
- [x] Add stage component (using existing image)
- [ ] Delete page

## Getting started

### 1. Python

First, make sure **Python 3.12** is installed in your system. Note that some of the libraries might not run correctly with the latest versions of python.

### 2. Dependencies

If needed, create a virtual environmet, activate it, and install the dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

If not present yet, create a `.env` file in the project root with the content below. In this file we specify tokens and urls to allow the Strapi agent to acsess a running htc instance and the OpenAI APIs.

> ⚠️ Never commit this file into the source code repository as it contains access tokens!

```bash
OPENAI_API_KEY=<your_openai_api_key>
STRAPI_API_KEY=<your_strapi_api_key>
STRAPI_API_URL=<your_strapi_api_url>
LANGCHAIN_API_KEY=<your_langchain_api_key> #optional
```

### 3. Run

You can run the Strapi agent as **Web UI** or as a **Console App**

```bash
python web_app.py # Web UI
# or
python langchain_strapi_assistant.py # Console App
```

### 4. Debug (VisualStudio Code)

To debug the application on VisualStudio Code, use the default *debug* section and select *Console App*, or *Web UI* from the list.

## Troubleshooting

- **Python Version Compatibility**: Currently, the project has been tested on **Python 3.12**. With other versions it might not work as expected or not run at all.
- **API Key Issues**: If you encounter authorization errors, verify that the `.env` file contains the correct API keys.
- **Cache Issues**: Restart your environment and reload .env variables if necessary.

## Suggestions for Future Enhancements

- Persist comapny profile description.
- Multi agent architecture to handle different steps. E.g. initial validation, design set up, website editing.
