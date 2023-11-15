    def map_network(self, pool_size=255):
        """
        Maps the network
        :param pool_size: amount of parallel ping processes
        :return: list of valid ip addresses
        """
        if not self.ping:
            print("Error: `ping` executable not found. Please enter the IP "
                  "address in the text box manually")
            return
        ip_list = list()

        # get my IP and compose a base like 192.168.1.xxx
        ip_parts = self.get_my_ip().split('.')
        base_ip = ip_parts[0] + '.' + ip_parts[1] + '.' + ip_parts[2] + '.'

        # prepare the jobs queue
        try:
            jobs = multiprocessing.Queue()
            results = multiprocessing.Queue()

            pool = [multiprocessing.Process(target=self.pinger, args=(
                    jobs, results)) for _ in range(pool_size)]
        except PermissionError:
            print("The current system of packaging of guiscrcpy does not "
                  "support semaphores. Therefore its not possible to "
                  "multiprocess ip port scanning. Alternatively use `nmap` "
                  "or `nutty` to scan your network.")
            return

        for p in pool:
            p.start()

        # cue hte ping processes
        for i in range(1, 255):
            jobs.put(base_ip + '{0}'.format(i))

        for _ in pool:
            jobs.put(None)

        for p in pool:
            p.join()

        # collect he results
        while not results.empty():
            ip = results.get()
            ip_list.append(ip)

        return ip_list