# Chat with your middleware

A simple Proof of Concept (PoC) demonstrating how ChatGPT can serve as an interface to RESTful (OpenAPI) middleware systems. The context for the PoC is the airline industry.

## Abstract

Middleware in enterprise IT architectures is crucial, acting as the connective tissue between different internal and external systems, applications, storage solutions, and databases. It provides operational support, enabling the implementation of cross-domain business processes. This layer encompasses a range of services, APIs, queue systems, and more, facilitating seamless interactions across diverse IT environments.

Middleware can adopt various architectural patterns, such as Service-Oriented Architecture (SOA), microservices, or Enterprise Service Bus (ESB), sometimes integrating multiple approaches. It supports various message formats (e.g., SOAP, REST, gRPC, files) and operates over assorted technologies and protocols (e.g., web services, queuing and log systems, email, FTP). Primarily, middleware focuses on connectivity and reliability—often ensured by queuing or log systems like Kafka—without storing data itself.

As enterprises evolve, middleware platforms rapidly expand, incorporating an ever-increasing number of services and processes. This growth, while indicative of scalability, often leads to challenges in service identification and reuse. Moreover, the fragmentation and potential obsolescence of documentation, combined with knowledge silos, complicate the efficient leverage of existing capabilities.

This landscape complicates the introduction of new business processes, making it challenging to identify and utilize pre-existing services and workflows. This PoC introduces an innovative solution: interacting with middleware through conversational AI. This approach leverages technical documentation, such as OpenAPI definitions, and ChatGPT to:

1. Suggest relevant services for specific tasks.
2. Automate the execution of requests to these services to implement business flows.

This method not only streamlines the identification and utilization of middleware services but also enhances documentation accessibility and fosters a more dynamic, user-friendly approach to middleware interaction.

## Run the PoC

Install dependencies:

```bash
pip install pyyaml openai requests Flask
```
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

WebServer:

```text
* Serving Flask app 'app'
* Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server    instead.
* Running on http://127.0.0.1:5000
Press CTRL+C to quit
* Restarting with stat
* Debugger is active!
* Debugger PIN: 143-924-624
127.0.0.1 - - [27/Feb/2024 03:18:54] "GET /flight_schedule HTTP/1.1" 200 -
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

By calling these two API resources, you can successfully book a flight for a passenger and send a notification to    inform them about any updates related to their flight.
```
