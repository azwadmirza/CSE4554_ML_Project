def _start_cluster_process(endpoint, n_process, shared_memory, **kw):
    event = multiprocessing.Event()

    kw = kw.copy()
    kw['n_process'] = n_process
    kw['shared_memory'] = shared_memory or '20%'
    process = gipc.start_process(_start_cluster, args=(endpoint, event), kwargs=kw)

    while True:
        event.wait(5)
        if not event.is_set():
            # service not started yet
            continue
        if not process.is_alive():
            raise SystemError('New local cluster failed')
        else:
            break

    return process