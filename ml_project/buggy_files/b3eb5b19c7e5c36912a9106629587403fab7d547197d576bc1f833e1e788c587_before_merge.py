def get_queue_length(queue='celery'):
    with celery_app.connection_or_acquire() as conn:
        return conn.default_channel.queue_declare(
            queue=queue, durable=True, auto_delete=False
        ).message_count