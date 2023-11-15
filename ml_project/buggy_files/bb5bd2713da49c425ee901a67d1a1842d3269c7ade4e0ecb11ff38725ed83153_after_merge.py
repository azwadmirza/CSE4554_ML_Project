    def __get_process_stats(self, proc):
        """Get process stats."""
        procstat = {}

        # Process ID
        procstat['pid'] = proc.pid

        # Process name (cached by PSUtil)
        try:
            procstat['name'] = proc.name()
        except psutil.AccessDenied:
            procstat['name'] = ""

        # Process username (cached with internal cache)
        try:
            self.username_cache[procstat['pid']]
        except KeyError:
            try:
                self.username_cache[procstat['pid']] = proc.username()
            except (KeyError, psutil.AccessDenied):
                try:
                    self.username_cache[procstat['pid']] = proc.uids().real
                except (KeyError, AttributeError, psutil.AccessDenied):
                    self.username_cache[procstat['pid']] = "?"
        procstat['username'] = self.username_cache[procstat['pid']]

        # Process command line (cached with internal cache)
        try:
            self.cmdline_cache[procstat['pid']]
        except KeyError:
            # Patch for issue #391
            try:
                self.cmdline_cache[procstat['pid']] = ' '.join(proc.cmdline())
            except (AttributeError, psutil.AccessDenied, UnicodeDecodeError):
                self.cmdline_cache[procstat['pid']] = ""
        procstat['cmdline'] = self.cmdline_cache[procstat['pid']]

        # Process status
        procstat['status'] = str(proc.status())[:1].upper()

        # Process nice
        try:
            procstat['nice'] = proc.nice()
        except psutil.AccessDenied:
            procstat['nice'] = None

        # Process memory
        procstat['memory_info'] = proc.memory_info()
        procstat['memory_percent'] = proc.memory_percent()

        # Process CPU
        procstat['cpu_times'] = proc.cpu_times()
        procstat['cpu_percent'] = proc.cpu_percent(interval=0)

        # Process network connections (TCP and UDP) (Experimental)
        # REJECTED: Too high CPU consumption
        # try:
        #     procstat['tcp'] = len(proc.connections(kind="tcp"))
        #     procstat['udp'] = len(proc.connections(kind="udp"))
        # except:
        #     procstat['tcp'] = 0
        #     procstat['udp'] = 0

        # Process IO
        # procstat['io_counters'] is a list:
        # [read_bytes, write_bytes, read_bytes_old, write_bytes_old, io_tag]
        # If io_tag = 0 > Access denied (display "?")
        # If io_tag = 1 > No access denied (display the IO rate)
        # Note Disk IO stat not available on Mac OS
        if not is_mac:
            try:
                # Get the process IO counters
                proc_io = proc.io_counters()
                io_new = [proc_io.read_bytes, proc_io.write_bytes]
            except psutil.AccessDenied:
                # Access denied to process IO (no root account)
                # Put 0 in all values (for sort) and io_tag = 0 (for display)
                procstat['io_counters'] = [0, 0] + [0, 0]
                io_tag = 0
            else:
                # For IO rate computation
                # Append saved IO r/w bytes
                try:
                    procstat['io_counters'] = io_new + self.io_old[procstat['pid']]
                except KeyError:
                    procstat['io_counters'] = io_new + [0, 0]
                # then save the IO r/w bytes
                self.io_old[procstat['pid']] = io_new
                io_tag = 1

            # Append the IO tag (for display)
            procstat['io_counters'] += [io_tag]

        # SWAP memory
        # Only on Linux based OS
        # http://www.cyberciti.biz/faq/linux-which-process-is-using-swap/
        # REJECTED: Too high CPU consumption
        # if is_linux:
        #     logger.debug(proc.memory_maps())
        #     procstat['memory_swap'] = sum([ v.swap for v in proc.memory_maps() ])

        return procstat