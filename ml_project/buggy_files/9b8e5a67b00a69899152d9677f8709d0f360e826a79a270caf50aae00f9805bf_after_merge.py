    def __get_mandatory_stats(self, proc, procstat):
        """
        Get mandatory_stats: for all processes.
        Needed for the sorting/filter step.

        Stats grabbed inside this method:
        * 'name', 'cpu_times', 'status', 'ppid'
        * 'username', 'cpu_percent', 'memory_percent'
        """
        procstat['mandatory_stats'] = True

        # Name, cpu_times, status and ppid stats are in the same /proc file
        # Optimisation fir issue #958
        try:
            procstat.update(proc.as_dict(
                attrs=['name', 'cpu_times', 'status', 'ppid'],
                ad_value=''))
        except psutil.NoSuchProcess:
            # Try/catch for issue #432 (process no longer exist)
            return None
        else:
            procstat['status'] = str(procstat['status'])[:1].upper()

        try:
            procstat.update(proc.as_dict(
                attrs=['username', 'cpu_percent', 'memory_percent'],
                ad_value=''))
        except psutil.NoSuchProcess:
            # Try/catch for issue #432 (process no longer exist)
            return None

        if procstat['cpu_percent'] == '' or procstat['memory_percent'] == '':
            # Do not display process if we cannot get the basic
            # cpu_percent or memory_percent stats
            return None

        # Compute the maximum value for cpu_percent and memory_percent
        for k in self._max_values_list:
            if procstat[k] > self.get_max_values(k):
                self.set_max_values(k, procstat[k])

        # Process command line (cached with internal cache)
        if procstat['pid'] not in self.cmdline_cache:
            # Patch for issue #391
            try:
                self.cmdline_cache[procstat['pid']] = proc.cmdline()
            except (AttributeError, UnicodeDecodeError, psutil.AccessDenied, psutil.NoSuchProcess, psutil.WindowsError):
                self.cmdline_cache[procstat['pid']] = ""
        procstat['cmdline'] = self.cmdline_cache[procstat['pid']]

        # Process IO
        # procstat['io_counters'] is a list:
        # [read_bytes, write_bytes, read_bytes_old, write_bytes_old, io_tag]
        # If io_tag = 0 > Access denied (display "?")
        # If io_tag = 1 > No access denied (display the IO rate)
        # Availability: all platforms except macOS and Illumos/Solaris
        try:
            # Get the process IO counters
            proc_io = proc.io_counters()
            io_new = [proc_io.read_bytes, proc_io.write_bytes]
        except (psutil.AccessDenied, psutil.NoSuchProcess, NotImplementedError):
            # Access denied to process IO (no root account)
            # NoSuchProcess (process die between first and second grab)
            # Put 0 in all values (for sort) and io_tag = 0 (for display)
            procstat['io_counters'] = [0, 0] + [0, 0]
            io_tag = 0
        except AttributeError:
            return procstat
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

        return procstat