    def __init__(self):
        self.message_type = LiveActionDB
        self._shutdown = False
        self._pool = eventlet.GreenPool(size=cfg.CONF.scheduler.pool_size)
        self._coordinator = coordination_service.get_coordinator()