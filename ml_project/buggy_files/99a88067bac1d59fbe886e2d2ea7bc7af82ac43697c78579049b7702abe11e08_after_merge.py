def _start_cluster(endpoint, event, n_process=None, shared_memory=None, **kw):
    modules = kw.pop('modules', None) or []
    for m in modules:
        __import__(m, globals(), locals(), [])

    cluster = LocalDistributedCluster(endpoint, n_process=n_process,
                                      shared_memory=shared_memory, **kw)
    cluster.start_service()
    event.set()
    try:
        cluster.serve_forever()
    finally:
        cluster.stop_service()