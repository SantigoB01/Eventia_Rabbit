import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
        port=5672,
        credentials=pika.PlainCredentials("santiago_B", "password")
    )
)
channel = connection.channel()

# Declara una cola para asegurar que existe
channel.queue_declare(queue="prueba_cola")

# Envía un mensaje
channel.basic_publish(
    exchange="",
    routing_key="prueba_cola",
    body="Hola desde Python"
)

print("✅ Mensaje enviado a RabbitMQ")
connection.close()
