import os
import json
import sqlite3
import pika
from dotenv import load_dotenv


load_dotenv()

RABBIT_HOST = os.getenv("RABBIT_HOST", "localhost")
RABBIT_USER = os.getenv("RABBIT_USER", "santiago_B")
RABBIT_PASS = os.getenv("RABBIT_PASS", "password")
EXCHANGE = os.getenv("EXCHANGE", "bookings_exchange")

ARTIST_ID = "artist123"

DB_PATH = "artist_notifications.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id TEXT,
            client_name TEXT,
            client_contact TEXT,
            date TEXT,
            notes TEXT,
            received_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_notification(payload):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO notifications (artist_id, client_name, client_contact, date, notes, received_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (payload["artist_id"], payload["client_name"], payload["client_contact"], payload["date"], payload.get("notes", "")))
    conn.commit()
    conn.close()

def get_connection():
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    return pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)
    )

def main():
    init_db()
    conn = get_connection()
    channel = conn.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)

    queue_name = f"artist.{ARTIST_ID}.queue"
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=EXCHANGE, queue=queue_name, routing_key=f"artist.{ARTIST_ID}")

    print(f"[Worker] Escuchando solicitudes para: {ARTIST_ID}")

    def callback(ch, method, properties, body):
        payload = json.loads(body)
        print("[Worker] Notificación recibida:", payload)
        save_notification(payload)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()

if __name__ == "__main__":
    main()
