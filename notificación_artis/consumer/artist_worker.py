from flask import Flask, render_template, jsonify
import threading
import pika

app = Flask(__name__)

# Configuración RabbitMQ
RABBIT_HOST = "localhost"
RABBIT_USER = "santiago_B"
RABBIT_PASS = "password"
QUEUE_NAME = "artist_queue1"

# Lista en memoria para almacenar mensajes recibidos
mensajes_recibidos = []

def consumir_mensajes():
    """Consume mensajes de RabbitMQ y los guarda en la lista global"""
    def callback(ch, method, properties, body):
        mensaje = body.decode()
        print(f" [x] Recibido: {mensaje}")
        mensajes_recibidos.append(mensaje)

    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

    print(" [*] Esperando mensajes para el artista...")
    channel.start_consuming()

# Página principal -> usa artista.html
@app.route("/")
def artista_home():
    return render_template("artista.html")

# API que devuelve los mensajes
@app.route("/api/mensajes")
def api_mensajes():
    return {"mensajes": mensajes_recibidos}

if __name__ == "__main__":
    # Ejecutar el consumidor en un hilo aparte
    hilo = threading.Thread(target=consumir_mensajes, daemon=True)
    hilo.start()
    app.run(port=5001, debug=True)
