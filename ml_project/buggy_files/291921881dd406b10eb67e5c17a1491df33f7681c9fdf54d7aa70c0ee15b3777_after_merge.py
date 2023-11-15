    def __init__(self):
        self.main_loop = asyncio.get_event_loop()
        self.main_loop.create_task(self._handle_nsrunloop())
        self.main_loop.create_task(self._central_manager_delegate_ready())

        self.nsrunloop = NSRunLoop.currentRunLoop()

        self.central_manager_delegate = CentralManagerDelegate.alloc().init()