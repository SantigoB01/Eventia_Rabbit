from flask import Flask, render_template, request
import pika

app = Flask(__name__)

# Configuración de RabbitMQ
RABBIT_HOST = "localhost"
RABBIT_USER = "santiago_B"
RABBIT_PASS = "password"
QUEUE_NAME = "artist_queue1"

def send_message_to_queue(message: str):
    """Publica un mensaje en RabbitMQ"""
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=message)
    print(f" [x] Mensaje enviado: {message}")
    connection.close()

@app.route("/")
def index():
    return render_template("cliente.html")

@app.route("/send", methods=["POST"])
def send():
    artista = request.form.get("artista")
    fecha = request.form.get("fecha")
    cliente = request.form.get("cliente")

    mensaje = f"El cliente {cliente} quiere contratar a {artista} el día {fecha}"
    send_message_to_queue(mensaje)

    return f"✅ Mensaje enviado: {mensaje}"

if __name__ == "__main__":
    app.run(port=5000, debug=True)
