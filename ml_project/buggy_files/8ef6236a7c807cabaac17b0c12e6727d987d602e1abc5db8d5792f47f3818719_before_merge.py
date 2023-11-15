    def __init__(self):
        self.qemu = backend_pool.libvirt.backend_service.LibvirtBackendService()
        self.guests = []
        self.guest_id = 0
        self.guest_lock = Lock()

        # time in seconds between each loop iteration
        self.loop_sleep_time = 5
        self.loop_next_call = None

        # default configs; custom values will come from the client when they connect to the pool
        self.max_vm = 2
        self.vm_unused_timeout = 600
        self.share_guests = True

        # file configs
        self.ssh_port = CowrieConfig().getint('backend_pool', 'guest_ssh_port', fallback=-1)
        self.telnet_port = CowrieConfig().getint('backend_pool', 'guest_telnet_port', fallback=-1)

        # detect invalid config
        if not self.ssh_port > 0 and not self.telnet_port > 0:
            log.msg(eventid='cowrie.backend_pool.service',
                    format='Invalid configuration: one of SSH or Telnet ports must be defined!')
            os._exit(1)

        self.any_vm_up = False  # TODO fix for no VM available