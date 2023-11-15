    def __init__(self, *args, master_host, master_port, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = socket.gethostname() + "_" + uuid4().hex
        self.master_host = master_host
        self.master_port = master_port
        self.client = rpc.Client(master_host, master_port, self.client_id)
        self.greenlet.spawn(self.heartbeat)
        self.greenlet.spawn(self.worker)
        self.client.send(Message("client_ready", None, self.client_id))
        self.worker_state = STATE_INIT
        self.greenlet.spawn(self.stats_reporter)
        
        # register listener for when all locust users have hatched, and report it to the master node
        def on_hatch_complete(user_count):
            self.client.send(Message("hatch_complete", {"count":user_count}, self.client_id))
            self.worker_state = STATE_RUNNING
        self.environment.events.hatch_complete.add_listener(on_hatch_complete)
        
        # register listener that adds the current number of spawned locusts to the report that is sent to the master node 
        def on_report_to_master(client_id, data):
            data["user_count"] = self.user_count
        self.environment.events.report_to_master.add_listener(on_report_to_master)
        
        # register listener that sends quit message to master
        def on_quitting():
            self.client.send(Message("quit", None, self.client_id))
        self.environment.events.quitting.add_listener(on_quitting)

        # register listener thats sends locust exceptions to master
        def on_locust_error(locust_instance, exception, tb):
            formatted_tb = "".join(traceback.format_tb(tb))
            self.client.send(Message("exception", {"msg" : str(exception), "traceback" : formatted_tb}, self.client_id))
        self.environment.events.locust_error.add_listener(on_locust_error)