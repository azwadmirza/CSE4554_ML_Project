def watch_events(thread_map, event_stream, presenters, thread_args):
    crashed_containers = set()
    for event in event_stream:
        if event['action'] == 'stop':
            thread_map.pop(event['id'], None)

        if event['action'] == 'die':
            thread_map.pop(event['id'], None)
            crashed_containers.add(event['id'])

        if event['action'] != 'start':
            continue

        if event['id'] in thread_map:
            if thread_map[event['id']].is_alive():
                continue
            # Container was stopped and started, we need a new thread
            thread_map.pop(event['id'], None)

        # Container crashed so we should reattach to it
        if event['id'] in crashed_containers:
            event['container'].attach_log_stream()
            crashed_containers.remove(event['id'])

        thread_map[event['id']] = build_thread(
            event['container'],
            next(presenters),
            *thread_args
        )