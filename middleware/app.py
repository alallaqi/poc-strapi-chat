from flask import Flask, jsonify, request
import random
import string

app = Flask(__name__)

def random_string(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route('/flight_schedule', methods=['GET'])
def flight_schedule():
    flights = [
        {
            "flight_number": random_string(6),
            "departure_airport": "JFK",
            "arrival_airport": "LAX",
            "departure_time": "2024-03-01T10:00:00",
            "arrival_time": "2024-03-01T14:00:00"
        },
        {
            "flight_number": random_string(6),
            "departure_airport": "LAX",
            "arrival_airport": "JFK",
            "departure_time": "2024-03-02T12:00:00",
            "arrival_time": "2024-03-02T16:00:00"
        }
    ]
    return jsonify({"flights": flights})

@app.route('/passenger_notifications', methods=['POST'])
def passenger_notifications():
    data = request.json
    return jsonify({
        "status": "Notification sent successfully",
        "flight_number": data.get("flight_number"),
        "notification": data.get("notification")
    })

@app.route('/booking_services', methods=['POST'])
def booking_services():
    data = request.json
    return jsonify({
        "booking_reference": random_string(6),
        "passenger_name": data.get("passenger_name"),
        "flight_number": data.get("flight_number"),
        "seat_number": f"{random.randint(1, 30)}{'A' if random.random() < 0.5 else 'B'}"
    })

if __name__ == '__main__':
    app.run( port=8000, debug=True)
