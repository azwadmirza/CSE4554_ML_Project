    def update_local(self):
        """Update CPU stats using PSUtil."""
        # Grab CPU stats using psutil's cpu_percent and cpu_times_percent
        # Get all possible values for CPU stats: user, system, idle,
        # nice (UNIX), iowait (Linux), irq (Linux, FreeBSD), steal (Linux 2.6.11+)
        # The following stats are returned by the API but not displayed in the UI:
        # softirq (Linux), guest (Linux 2.6.24+), guest_nice (Linux 3.2.0+)
        self.stats['total'] = cpu_percent.get()
        cpu_times_percent = psutil.cpu_times_percent(interval=0.0)
        for stat in ['user', 'system', 'idle', 'nice', 'iowait',
                     'irq', 'softirq', 'steal', 'guest', 'guest_nice']:
            if hasattr(cpu_times_percent, stat):
                self.stats[stat] = getattr(cpu_times_percent, stat)

        # Additionnal CPU stats (number of events / not as a %)
        # ctx_switches: number of context switches (voluntary + involuntary) per second
        # interrupts: number of interrupts per second
        # soft_interrupts: number of software interrupts per second. Always set to 0 on Windows and SunOS.
        # syscalls: number of system calls since boot. Always set to 0 on Linux.
        try:
            cpu_stats = psutil.cpu_stats()
        except AttributeError:
            # cpu_stats only available with PSUtil 4.1 or +
            pass
        else:
            # By storing time data we enable Rx/s and Tx/s calculations in the
            # XML/RPC API, which would otherwise be overly difficult work
            # for users of the API
            time_since_update = getTimeSinceLastUpdate('cpu')

            # Previous CPU stats are stored in the cpu_stats_old variable
            if not hasattr(self, 'cpu_stats_old'):
                # First call, we init the cpu_stats_old var
                self.cpu_stats_old = cpu_stats
            else:
                for stat in cpu_stats._fields:
                    if getattr(cpu_stats, stat) is not None:
                        self.stats[stat] = getattr(cpu_stats, stat) - getattr(self.cpu_stats_old, stat)

                self.stats['time_since_update'] = time_since_update

                # Core number is needed to compute the CTX switch limit
                self.stats['cpucore'] = self.nb_log_core

                # Save stats to compute next step
                self.cpu_stats_old = cpu_stats