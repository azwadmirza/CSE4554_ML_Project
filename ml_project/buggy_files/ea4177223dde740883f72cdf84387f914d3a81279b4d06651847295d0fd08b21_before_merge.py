def generate_show_queue():
    """
    Generate a JSON-pickable list of items in the show queue.

    :returns: list of show queue items
    """
    if not app.show_queue_scheduler:
        return []

    queue = app.show_queue_scheduler.action.queue
    if app.show_queue_scheduler.action.currentItem is not None:
        queue.insert(0, app.show_queue_scheduler.action.currentItem)

    return [_queued_show_to_json(item) for item in queue]