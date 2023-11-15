def _start_web_process(scheduler_endpoint, web_endpoint):
    ui_port = int(web_endpoint.rsplit(':', 1)[1])

    web_event = _mp_spawn_context.Event()
    web_process = _mp_spawn_context.Process(
        target=_start_web, args=(scheduler_endpoint, ui_port, web_event), daemon=True)
    web_process.start()

    while True:
        web_event.wait(5)
        if not web_event.is_set():
            # web not started yet
            continue
        if not web_process.is_alive():
            raise SystemError('New web interface failed')
        else:
            break

    return web_process