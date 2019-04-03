#!/usr/bin/env python3
import pika


HOST_ADDR = 'localhost'
QUEUE = 'csdndata'
ROUTING_KEY = 'csdndata'


def callback(ch, method, properties, body):
    body = body.decode()
    if body == "quit":
        ch.basic_cancel(consumer_tag=ROUTING_KEY)
        ch.stop_consuming()
    else:
        print(" [x] Received %r" % body)


def rabbitmq_init(queue=QUEUE):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=HOST_ADDR))
    channel = connection.channel()

    channel.queue_declare(queue=queue)

    return connection, channel


def worker_be_consumer():
    connection, channel = rabbitmq_init()

    channel.basic_consume(
        queue=QUEUE, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages......')
    print('\tTo exit press CTRL+C, or send "quit" message')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.basic_cancel(consumer_tag=ROUTING_KEY)
        channel.stop_consuming()


def main():
    worker_be_consumer()


if __name__ == '__main__':
    main()
