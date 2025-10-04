import os
import json
from flask import Flask, request, jsonify
import pika
from dotenv import load_dotenv

load_dotenv()

RABBIT_HOST = os.getenv("RABBIT_HOST", "localhost")
RABBIT_USER = os.getenv("RABBIT_USER", "santiago_B")
RABBIT_PASS = os.getenv("RABBIT_PASS", "password")
EXCHANGE = os.getenv("EXCHANGE", "bookings_exchange")

app = Flask(__name__)

def get_connection():
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    params = pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)
    return pika.BlockingConnection(params)

@app.route("/book", methods=["POST"])
def book_artist():
    data = request.get_json()
    required = ["artist_id", "client_name", "client_contact", "date"]
    for r in required:
        if r not in data:
            return jsonify({"error": f"missing field {r}"}), 400

    message = {
        "artist_id": data["artist_id"],
        "client_name": data["client_name"],
        "client_contact": data["client_contact"],
        "date": data["date"],
        "notes": data.get("notes", "")
    }
    routing_key = f"artist.{data['artist_id']}"

    conn = get_connection()
    channel = conn.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)

    channel.basic_publish(
        exchange=EXCHANGE,
        routing_key=routing_key,
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    conn.close()
    return jsonify({"status": "sent", "artist_id": data["artist_id"]}), 201

if __name__ == "__main__":
    app.run(debug=True, port=5000)