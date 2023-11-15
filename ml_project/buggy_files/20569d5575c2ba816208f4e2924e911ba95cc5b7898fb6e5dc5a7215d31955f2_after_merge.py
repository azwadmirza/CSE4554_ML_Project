    def __init__(self, destination_vip, destination_serverkey,
                 destination_historian_identity=PLATFORM_HISTORIAN,
                 **kwargs):
        """
        
        :param destination_vip: vip address of the destination volttron 
        instance
        :param destination_serverkey: public key of the destination server
        :param services_topic_list: subset of topics that are inherently 
        supported by base historian. Default is device, analysis, logger, 
        and record topics
        :param custom_topic_list: any additional topics this historian 
        should subscribe to.
        :param destination_historian_identity: vip identity of the 
        destination historian. default is 'platform.historian'
        :param kwargs: additional arguments to be passed along to parent class
        """
        kwargs["process_loop_in_greenlet"] = True
        super(DataMover, self).__init__(**kwargs)
        self.destination_vip = destination_vip
        self.destination_serverkey = destination_serverkey
        self.destination_historian_identity = destination_historian_identity

        config = {"destination_vip":self.destination_vip,
                  "destination_serverkey": self.destination_serverkey,
                  "destination_historian_identity": self.destination_historian_identity}

        self.update_default_config(config)

        # will be available in both threads.
        self._last_timeout = 0