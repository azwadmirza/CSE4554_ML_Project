    def update(self):
        """Update swap memory stats using the input method."""
        # Init new stats
        stats = self.get_init_value()

        if self.input_method == 'local':
            # Update stats using the standard system lib
            # Grab SWAP using the psutil swap_memory method
            try:
                sm_stats = psutil.swap_memory()
            except RuntimeError:
                # Crash on startup on Illumos when no swap is configured #1767
                pass
            else:
                # Get all the swap stats (copy/paste of the psutil documentation)
                # total: total swap memory in bytes
                # used: used swap memory in bytes
                # free: free swap memory in bytes
                # percent: the percentage usage
                # sin: the number of bytes the system has swapped in from disk (cumulative)
                # sout: the number of bytes the system has swapped out from disk
                # (cumulative)
                for swap in ['total', 'used', 'free', 'percent',
                            'sin', 'sout']:
                    if hasattr(sm_stats, swap):
                        stats[swap] = getattr(sm_stats, swap)
        elif self.input_method == 'snmp':
            # Update stats using SNMP
            if self.short_system_name == 'windows':
                # Mem stats for Windows OS are stored in the FS table
                try:
                    fs_stat = self.get_stats_snmp(snmp_oid=snmp_oid[self.short_system_name],
                                                  bulk=True)
                except KeyError:
                    self.reset()
                else:
                    for fs in fs_stat:
                        # The virtual memory concept is used by the operating
                        # system to extend (virtually) the physical memory and
                        # thus to run more programs by swapping unused memory
                        # zone (page) to a disk file.
                        if fs == 'Virtual Memory':
                            stats['total'] = int(
                                fs_stat[fs]['size']) * int(fs_stat[fs]['alloc_unit'])
                            stats['used'] = int(
                                fs_stat[fs]['used']) * int(fs_stat[fs]['alloc_unit'])
                            stats['percent'] = float(
                                stats['used'] * 100 / stats['total'])
                            stats['free'] = stats['total'] - stats['used']
                            break
            else:
                stats = self.get_stats_snmp(snmp_oid=snmp_oid['default'])

                if stats['total'] == '':
                    self.reset()
                    return stats

                for key in iterkeys(stats):
                    if stats[key] != '':
                        stats[key] = float(stats[key]) * 1024

                # used=total-free
                stats['used'] = stats['total'] - stats['free']

                # percent: the percentage usage calculated as (total -
                # available) / total * 100.
                stats['percent'] = float(
                    (stats['total'] - stats['free']) / stats['total'] * 100)

        # Update the stats
        self.stats = stats

        return self.stats