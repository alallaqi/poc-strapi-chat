from flask import Flask, jsonify, request

app = Flask(__name__)

# Define dummy data
flights = [
  {
    "flightNumber": "AB1234",
    "departureTime": "2022-01-01T10:00:00Z",
    "departureAirport": "FCO",
    "arrivalTime": "2022-01-01T12:00:00Z",
    "arrivalAirport": "ZRH"
  },
  {
    "flightNumber": "CD5678",
    "departureTime": "2022-01-02T14:00:00Z",
    "departureAirport": "ZRH",
    "arrivalTime": "2022-01-02T16:00:00Z",
    "arrivalAirport": "FCO"
  }
]

bookings = [
  {
    "code": "BK1234",
    "passenger": {
      "name": "John Doe",
      "email": "john.doe@example.com"
    },
    "flight": {
      "flightNumber": "AB1234",
      "departureTime": "2022-01-01T10:00:00Z",
      "departureAirport": "FCO",
      "arrivalTime": "2022-01-01T12:00:00Z",
      "arrivalAirport": "ZRH"
    }
  }
]

notifications = [
  {
    "message": "Gate changed.",
    "passenger": {
      "name": "John Doe",
      "email": "john.doe@example.com"
    }
  }
]

# Define routes
@app.route('/flight/scheduleByDates', methods=['GET'])
def get_flights():
  start_date = request.args.get('startDate')
  end_date = request.args.get('endDate')
  # Filter flights based on start_date and end_date if needed
  return jsonify(flights)

@app.route('/booking', methods=['POST'])
def create_booking():
  # Create a new booking based on the request body
  booking = request.json
  bookings.append(booking)
  return jsonify(booking), 200

@app.route('/booking/findByFLight', methods=['GET'])
def search_bookings_by_flight():
  flight_number = request.args.get('flightNumber')
  departure_time = request.args.get('departureTime')
  departure_airport = request.args.get('departureAirport')
  arrival_time = request.args.get('arrivalTime')
  arrival_airport = request.args.get('arrivalAirport')
  # Filter bookings based on flight details if needed
  return jsonify(bookings)

@app.route('/passenger/notify', methods=['POST'])
def notify_passenger():
  notification = request.json
  notifications.append(notification)
  return jsonify(notification), 200

if __name__ == '__main__':
  app.run()
