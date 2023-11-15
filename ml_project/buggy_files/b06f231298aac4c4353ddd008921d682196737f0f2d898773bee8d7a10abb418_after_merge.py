    def update(self):
        """
        Update the processes stats
        """
        # Reset the stats
        self.processlist = []
        self.processcount = {'total': 0, 'running': 0, 'sleeping': 0, 'thread': 0}

        # Do not process if disable tag is set
        if self.disable_tag:
            return

        # Get the time since last update
        time_since_update = getTimeSinceLastUpdate('process_disk')

        # Build an internal dict with only mandatories stats (sort keys)
        processdict = {}
        for proc in psutil.process_iter():
            # If self.get_max_processes() is None: Only retreive mandatory stats
            # Else: retreive mandatory and standard stats
            s = self.__get_process_stats(proc, 
                                         mandatory_stats=True, 
                                         standard_stats=self.get_max_processes() is None)
            # Continue to the next process if it has to be filtered
            if s is None or (self.is_filtered(s['cmdline']) and self.is_filtered(s['name'])):
                continue
            # Ok add the process to the list
            processdict[proc] = s
            # ignore the 'idle' process on Windows and *BSD
            # ignore the 'kernel_task' process on OS X
            # waiting for upstream patch from psutil
            if (is_bsd and processdict[proc]['name'] == 'idle' or
                is_windows and processdict[proc]['name'] == 'System Idle Process' or
                is_mac and processdict[proc]['name'] == 'kernel_task'):
                continue
            # Update processcount (global statistics)
            try:
                self.processcount[str(proc.status())] += 1
            except KeyError:
                # Key did not exist, create it
                self.processcount[str(proc.status())] = 1
            else:
                self.processcount['total'] += 1
            # Update thread number (global statistics)
            try:
                self.processcount['thread'] += proc.num_threads()
            except:
                pass

        # Process optimization
        # Only retreive stats for visible processes (get_max_processes)
        if self.get_max_processes() is not None:
            # Sort the internal dict and cut the top N (Return a list of tuple)
            # tuple=key (proc), dict (returned by __get_process_stats)
            try:
                processiter = sorted(processdict.items(), key=lambda x: x[1][self.getsortkey()], reverse=True)
            except TypeError:
                # Fallback to all process (issue #423)
                processloop = processdict.items()
                first = False
            else:
                processloop = processiter[0:self.get_max_processes()]
                first = True
        else:
            # Get all processes stats
            processloop = processdict.items()
            first = False        
        for i in processloop:
            # Already existing mandatory stats
            procstat = i[1]
            if self.get_max_processes() is not None:
                # Update with standard stats
                # and extended stats but only for TOP (first) process
                s = self.__get_process_stats(i[0], 
                                             mandatory_stats=False, 
                                             standard_stats=True,
                                             extended_stats=first)
                if s is None:
                    continue
                procstat.update(s)
            # Add a specific time_since_update stats for bitrate
            procstat['time_since_update'] = time_since_update
            # Update process list
            self.processlist.append(procstat)
            # Next...
            first = False

        # Clean internals caches if timeout is reached
        if self.cache_timer.finished():
            self.username_cache = {}
            self.cmdline_cache = {}
            # Restart the timer
            self.cache_timer.reset()