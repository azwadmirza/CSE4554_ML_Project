    def update(self):
        """Update the command result attributed."""
        # Search application monitored processes by a regular expression
        processlist = glances_processes.getalllist()

        # Iter upon the AMPs dict
        for k, v in iteritems(self.get()):
            try:
                amps_list = [p for p in processlist for c in p['cmdline'] if re.search(v.regex(), c) is not None]
            except TypeError:
                continue
            if len(amps_list) > 0:
                # At least one process is matching the regex
                logger.debug("AMPS: {} process detected (PID={})".format(k, amps_list[0]['pid']))
                # Call the AMP update method
                thread = threading.Thread(target=v.update_wrapper, args=[amps_list])
                thread.start()
            else:
                # Set the process number to 0
                v.set_count(0)
                if v.count_min() is not None and v.count_min() > 0:
                    # Only display the "No running process message" is countmin is defined
                    v.set_result("No running process")

        return self.__amps_dict