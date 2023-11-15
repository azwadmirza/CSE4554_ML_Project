    def update(self):
        """Update the processes stats."""
        # Reset the stats
        self.processlist = []
        self.reset_processcount()

        # Do not process if disable tag is set
        if self.disable_tag:
            return

        # Time since last update (for disk_io rate computation)
        time_since_update = getTimeSinceLastUpdate('process_disk')

        # Grab standard stats
        #####################
        standard_attrs = ['cmdline', 'cpu_percent', 'cpu_times', 'memory_info',
                          'memory_percent', 'name', 'nice', 'pid', 'ppid',
                          'status', 'username', 'status', 'num_threads']
        # io_counters availability: Linux, BSD, Windows, AIX
        if not MACOS and not SUNOS:
            standard_attrs += ['io_counters']
        # gids availability: Unix
        if not WINDOWS:
            standard_attrs += ['gids']

        # and build the processes stats list (psutil>=5.3.0)
        self.processlist = [p.info for p in psutil.process_iter(attrs=standard_attrs, ad_value=None)
                            # OS-related processes filter
                            if not (BSD and p.info['name'] == 'idle') and
                            not (WINDOWS and p.info['name'] == 'System Idle Process') and
                            not (MACOS and p.info['name'] == 'kernel_task') and
                            # Kernel threads filter
                            not (self.no_kernel_threads and LINUX and p.info['gids'].real == 0) and
                            # User filter
                            not (self._filter.is_filtered(p.info))]

        # Sort the processes list by the current sort_key
        self.processlist = sort_stats(self.processlist,
                                      sortedby=self.sort_key,
                                      reverse=True)

        # Update the processcount
        self.update_processcount(self.processlist)

        # Loop over processes and add metadata
        first = True
        for proc in self.processlist:
            if first and not self.disable_extended_tag:
                # Get extended stats, only for top processes (see issue #403).
                # - cpu_affinity (Linux, Windows, FreeBSD)
                # - ionice (Linux and Windows > Vista)
                # - memory_full_info (Linux)
                # - num_ctx_switches (not available on Illumos/Solaris)
                # - num_fds (Unix-like)
                # - num_handles (Windows)
                # - num_threads (not available on *BSD)
                # - memory_maps (only swap, Linux)
                #   https://www.cyberciti.biz/faq/linux-which-process-is-using-swap/
                # - connections (TCP and UDP)
                extended = {}
                try:
                    top_process = psutil.Process(proc['pid'])
                    extended_stats = ['cpu_affinity', 'ionice',
                                      'memory_full_info', 'num_ctx_switches',
                                      'num_fds', 'num_threads']
                    if WINDOWS:
                        extended_stats += ['num_handles']
                    extended = top_process.as_dict(attrs=extended_stats)
                    if LINUX:
                        try:
                            extended['memory_swap'] = sum([v.swap for v in top_process.memory_maps()])
                        except psutil.NoSuchProcess:
                            pass
                        except (psutil.AccessDenied, NotImplementedError):
                            # NotImplementedError: /proc/${PID}/smaps file doesn't exist
                            # on kernel < 2.6.14 or CONFIG_MMU kernel configuration option
                            # is not enabled (see psutil #533/glances #413).
                            extended['memory_swap'] = None
                    try:
                        extended['tcp'] = len(top_process.connections(kind="tcp"))
                        extended['udp'] = len(top_process.connections(kind="udp"))
                    except psutil.AccessDenied:
                        extended['tcp'] = None
                        extended['udp'] = None
                except (psutil.NoSuchProcess, ValueError, AttributeError) as e:
                    logger.error('Can not grab extended stats ({})'.format(e))
                    extended['extended_stats'] = False
                else:
                    logger.debug('Grab extended stats for process {}'.format(proc['pid']))
                    extended['extended_stats'] = True
                proc.update(extended)
            first = False

            # Time since last update (for disk_io rate computation)
            proc['time_since_update'] = time_since_update

            # Process status (only keep the first char)
            proc['status'] = str(proc['status'])[:1].upper()

            # Process IO
            # procstat['io_counters'] is a list:
            # [read_bytes, write_bytes, read_bytes_old, write_bytes_old, io_tag]
            # If io_tag = 0 > Access denied or first time (display "?")
            # If io_tag = 1 > No access denied (display the IO rate)
            if 'io_counters' in proc and proc['io_counters'] is not None:
                io_new = [proc['io_counters'].read_bytes,
                          proc['io_counters'].write_bytes]
                # For IO rate computation
                # Append saved IO r/w bytes
                try:
                    proc['io_counters'] = io_new + self.io_old[proc['pid']]
                    io_tag = 1
                except KeyError:
                    proc['io_counters'] = io_new + [0, 0]
                    io_tag = 0
                # then save the IO r/w bytes
                self.io_old[proc['pid']] = io_new
            else:
                proc['io_counters'] = [0, 0] + [0, 0]
                io_tag = 0
            # Append the IO tag (for display)
            proc['io_counters'] += [io_tag]

        # Compute the maximum value for keys in self._max_values_list (CPU, MEM)
        for k in self._max_values_list:
            if self.processlist != []:
                self.set_max_values(k, max(i[k] for i in self.processlist
                if not (i[k] == None)))