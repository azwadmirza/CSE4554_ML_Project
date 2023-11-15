    def update(self):
        """Update CPU stats using the input method."""
        # Reset stats
        self.reset()

        # Grab CPU stats using psutil's cpu_percent and cpu_times_percent methods
        if self.get_input() == 'local':
            # Get all possible values for CPU stats: user, system, idle,
            # nice (UNIX), iowait (Linux), irq (Linux, FreeBSD), steal (Linux 2.6.11+)
            # The following stats are returned by the API but not displayed in the UI:
            # softirq (Linux), guest (Linux 2.6.24+), guest_nice (Linux 3.2.0+)
            self.stats['total'] = psutil.cpu_percent(interval=0.0)
            cpu_times_percent = psutil.cpu_times_percent(interval=0.0)
            for stat in ['user', 'system', 'idle', 'nice', 'iowait',
                         'irq', 'softirq', 'steal', 'guest', 'guest_nice']:
                if hasattr(cpu_times_percent, stat):
                    self.stats[stat] = getattr(cpu_times_percent, stat)
        elif self.get_input() == 'snmp':
            # Update stats using SNMP
            if self.get_short_system_name() in ('windows', 'esxi'):
                # Windows or VMWare ESXi
                # You can find the CPU utilization of windows system by querying the oid
                # Give also the number of core (number of element in the table)
                try:
                    cpu_stats = self.set_stats_snmp(snmp_oid=snmp_oid[self.get_short_system_name()],
                                                    bulk=True)
                except KeyError:
                    self.reset()

                # Iter through CPU and compute the idle CPU stats
                self.stats['nb_log_core'] = 0
                self.stats['idle'] = 0
                for c in cpu_stats:
                    if c.startswith('percent'):
                        self.stats['idle'] += float(cpu_stats['percent.3'])
                        self.stats['nb_log_core'] += 1
                if self.stats['nb_log_core'] > 0:
                    self.stats['idle'] = self.stats['idle'] / self.stats['nb_log_core']
                self.stats['idle'] = 100 - self.stats['idle']

            else:
                # Default behavor
                try:
                    self.stats = self.set_stats_snmp(snmp_oid=snmp_oid[self.get_short_system_name()])
                except KeyError:
                    self.stats = self.set_stats_snmp(snmp_oid=snmp_oid['default'])

                if self.stats['idle'] == '':
                    self.reset()
                    return self.stats

                # Convert SNMP stats to float
                for key in list(self.stats.keys()):
                    self.stats[key] = float(self.stats[key])

        # Update the history list
        self.update_stats_history()

        return self.stats