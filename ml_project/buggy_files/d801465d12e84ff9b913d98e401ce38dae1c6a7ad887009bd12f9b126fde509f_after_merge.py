    def getProcessList(self, sortedby='auto'):
        """
        Return the sorted process list
        """

        if not process_tag:
            return []
        if self.process == {} or 'limits' not in globals():
            return self.process

        sortedReverse = True
        if sortedby == 'auto':
            # Auto selection (default: sort by CPU%)
            sortedby = 'cpu_percent'
            # Dynamic choice
            if ('iowait' in self.cpu and
                self.cpu['iowait'] > limits.getCPUWarning(stat='iowait')):
                # If CPU IOWait > 70% sort by IORATE usage
                sortedby = 'io_counters'
            elif (self.mem['total'] != 0 and
                  self.mem['used'] * 100 / self.mem['total'] > limits.getMEMWarning()):
                # If global MEM > 70% sort by MEM usage
                sortedby = 'memory_percent'
        elif sortedby == 'name':
            sortedReverse = False

        if sortedby == 'io_counters':
            try:
                # Sort process by IO rate (sum IO read + IO write)
                listsorted = sorted(self.process,
                                    key=lambda process: process[sortedby][0] -
                                    process[sortedby][2] + process[sortedby][1] -
                                    process[sortedby][3], reverse=sortedReverse)
            except:
                listsorted = sorted(self.process, key=lambda process: process['cpu_percent'],
                                    reverse=sortedReverse)                
        else:
            # Others sorts
            listsorted = sorted(self.process, key=lambda process: process[sortedby],
                                reverse=sortedReverse)

        # Save the latest sort type in a global var
        self.process_list_sortedby = sortedby

        # Return the sorted list
        return listsorted