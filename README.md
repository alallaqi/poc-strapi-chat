# Chatting With The Middleware! (LangChain + OpenAPI + LLM)


📄 Full article on Medium: [Chatting With The Middleware!. How conversational AI can change the interface to middlware platfoms](https://medium.com/@franco.dgstn/chatting-with-the-middleware-6c2bc115daac)

A simple Proof of Concept (PoC) demonstrating how ChatGPT can serve as an interface to RESTful (OpenAPI) middleware systems. The PoC includes a few dummy airlines related API exposed on a local test server and uses **LangChain** + **OpenAPI** integration to identify resources and execute calls. The PoC uses **OpenAI gpt-4** as LLM.

The PoC is only itended as simple demonstration. See [OpenAPI | 🦜️🔗 Langchain](https://python.langchain.com/docs/integrations/toolkits/openapi) for more details.

## PoC

Install dependencies:

```bash
pip install -r requirements.txt
```

On a separate terminal, run the mock middleware (a Flask instance which exposes a few operations returning mocked data):

```bash
python ./middleware/app.py
```

Run the middleware assistant

```bash
python langchain_middleware_assistant.py
```

Sample prompt:

```text
Book a flight from ZRH to FCO for the passenger John Doe and send a notification. 
```

Assistant (LangChain + OpenAPI + LLM):

- Planner - Identify the resources and parameters.
- Controller - Execute API calls.

```text
> Entering new AgentExecutor chain...
Action: api_planner
Action Input: Book a flight from ZRH to FCO for the passenger John Doe and send a notification.
Observation: 
1. GET /flight/scheduleByDates with query params to search for flights from ZRH to FCO
2. POST /booking to place a new booking for John Doe on the selected flight
3. POST /passenger/notify to send a notification to John Doe about the booking.
Thought:I'm ready to execute the API calls.
Action: api_controller
Action Input:
1. GET /flight/scheduleByDates with query params to search for flights from ZRH to FCO 
2. POST /booking to place a new booking for John Doe on the selected flight
3. POST /passenger/notify to send a notification to John Doe about the booking.

> Entering new AgentExecutor chain...
I need to start by making a GET request to /flight/scheduleByDates to fetch the flight schedules. However, the API O.

Action: requests_get
Action Input: 
{
  "url": "http://localhost:5000/flight/scheduleByDates",
  "params": {},
  "output_instructions": "Extract all flights from ZRH to FCO"
}
Observation: Flight Number: AB1234, Departure Time: 2022-01-01T10:00:00Z, Arrival Time: 2022-01-01T12:00:00Z       
Thought:I have successfully fetched the flight schedules. The flight from ZRH to FCO is AB1234, departing at 2022-01-01T10:00:00Z and arriving at 2022-01-01T12:00:00Z. Now, I will make a POST request to /booking to place a new booking for John Doe on this flight.

Action: requests_post
Action Input: 
{
  "url": "http://localhost:5000/booking",
  "data": {
    "code": "JD123",
    "flight": {
      "arrivalAirport": "FCO",
      "arrivalTime": "2022-01-01T12:00:00Z",
      "departureAirport": "ZRH",
      "departureTime": "2022-01-01T10:00:00Z",
      "flightNumber": "AB1234"
    },
    "passenger": {
      "email": "john.doe@example.com",
      "name": "John Doe"
    }
  },
  "output_instructions": "Extract the booking code"
}
Observation: JD123
Thought:I have successfully placed a booking for John Doe on flight AB1234 from ZRH to FCO. The booking code is JD123. Now, I will make a POST request to /passenger/notify to send a notification to John Doe about the booking.     

Action: requests_post
Action Input: 
{
  "url": "http://localhost:5000/passenger/notify",
  "data": {
    "message": "Your booking on flight AB1234 from ZRH to FCO has been confirmed. Your booking code is JD123.",    
    "passenger": {
      "email": "john.doe@example.com",
      "name": "John Doe"
    }
  },
  "output_instructions": "Extract the message"
}
Observation: "Your booking on flight AB1234 from ZRH to FCO has been confirmed. Your booking code is JD123."       
Thought:I have successfully sent a notification to John Doe about his booking. The message is "Your booking on flight AB1234 from ZRH to FCO has been confirmed. Your booking code is JD123." I am finished executing the plan.       

Final Answer: The booking for John Doe on flight AB1234 from ZRH to FCO has been confirmed. The booking code is JD123. A notification with this information has been sent to John Doe.

> Finished chain.

Observation: The booking for John Doe on flight AB1234 from ZRH to FCO has been confirmed. The booking code is JD123. A notification with this information has been sent to John Doe.
Thought:I am finished executing a plan and have the information the user asked for.
Final Answer: The booking for John Doe on flight AB1234 from ZRH to FCO has been confirmed. The booking code is JD123. A notification with this information has been sent to John Doe.

> Finished chain.
```
