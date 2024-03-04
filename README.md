# Chat with your middleware

A simple Proof of Concept (PoC) demonstrating how ChatGPT can serve as an interface to RESTful (OpenAPI) middleware systems. The context for the PoC is the airline industry.

> _The PoC is only itended as quick demostration. For real usecases, OpenAI offers specific functions calling APIs. See: [How to call functions with chat models | OpenAI Cookbook](https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models)._

## PoC

📄 Full article on Medium: [Chatting With The Middleware!. How conversational AI can change the interface to middlware platfoms](https://medium.com/@franco.dgstn/chatting-with-the-middleware-6c2bc115daac)

### Abstract

In the intricate and dynamic landscape of large enterprises, integrating middleware platforms with conversational artificial intelligence (AI) offers a promising pathway to boost operational efficiency and foster innovation. This article delves into the potential of employing conversational AI for simplifying interactions with middleware systems, proposing an innovative approach that leverages intuitive dialogue interfaces for system navigation, documentation, and process streamlining. While using the airline industry as an illustrative example, the discussion extends to a broader application spectrum, emphasizing the facilitation of interface discovery, the enablement of low-code solutions for business process implementation, and the acceleration of prototype development and integration. The discussion acknowledges the inherent challenges such as maintaining up-to-date and comprehensive technical documentation, managing the complexity of extensive service landscapes, and ensuring reliability in mission-critical applications. Highlighting the transformative possibilities of conversational AI in middleware management, the article is enriched with a practical demonstration through a basic PoC, which is available on GitHub at francodgstn/poc-mdw-chat (github.com), offering a tangible insight into how conversational AI can revolutionize middleware interactions. This comprehensive exploration sets the groundwork for future advancements in enterprise technology strategies, indicating a significant shift towards more interactive and efficient middleware engagements.

## Run the PoC

Install dependencies:

```bash
pip install -r requirements.txt
```

On a separate terminal, run the mock middleware (a Flask instance which exposes a few operations returning mocked data):

```bash
python ./middleware/app.py
```

### Usecase

### Use Case: Suggesting and Executing Requests

> Currently only calls the first suggested resource, without passing any parameter

```bash
python run_api.py
```

Assistant:

```text
[Middlware Assistant] Please enter your message (or type 'quit' to exit):
I want to know the flight schedule

Suggestion:
Based on your input 'I want to know the flight schedule', the most appropriate resource to call would be /   flight_schedule using the GET method.

API Response:
{
  "flights": [
    {
      "arrival_airport": "LAX",
      "arrival_time": "2024-03-01T14:00:00",
      "departure_airport": "JFK",
      "departure_time": "2024-03-01T10:00:00",
      "flight_number": "MBAYWJ"
    },
    {
      "arrival_airport": "JFK",
      "arrival_time": "2024-03-02T16:00:00",
      "departure_airport": "LAX",
      "departure_time": "2024-03-02T12:00:00",
      "flight_number": "3HPBR3"
    }
  ]
}
```

### Usecase: Getting Suggestion Formatted as Markdown

```bash
python suggest_api.py
```

```text
[Middlware Assistant] Please enter your message (or type 'quit' to exit):
I want to book a flight and send a notification, show the suggestions in markdown format


Answer:
Based on the provided API resources, the most appropriate OpenAPI resources to call for booking a flight and    sending a notification would be:

1. **Book a Flight:**
  - **Path:** /booking_services
  - **Method:** POST
  - **Summary:** Book a Flight
  - **Description:** Book a flight for a passenger.
  - **Example Request:**
    ```json
    {
      "passenger_name": "John Doe",
      "flight_number": "XYZ789",
      "seat_preference": "Window"
    }
    ```
  - **Example Response:**
    ```json
    {
      "booking_reference": "BK123",
      "passenger_name": "John Doe",
      "flight_number": "XYZ789",
      "seat_number": "23A"
    }
    ```

2. **Send Passenger Notification:**
  - **Path:** /passenger_notifications
  - **Method:** POST
  - **Summary:** Send Passenger Notification
  - **Description:** Send notifications to passengers about flight updates.
  - **Example Request:**
    ```json
    {
      "flight_number": "ABC123",
      "notification": "Your flight has been delayed."
    }
    ```
  - **Example Response:**
    ```json
    {
      "status": "Notification sent successfully"
    }
    ```

By calling these two API resources, you can successfully book a flight for a passenger and send a notification to inform them about any updates related to their flight.
```
