    def update(self):
        """Update quicklook stats using the input method."""
        # Init new stats
        stats = self.get_init_value()

        # Grab quicklook stats: CPU, MEM and SWAP
        if self.input_method == 'local':
            # Get the latest CPU percent value
            stats['cpu'] = cpu_percent.get()
            stats['percpu'] = cpu_percent.get(percpu=True)
            # Use the psutil lib for the memory (virtual and swap)
            stats['mem'] = psutil.virtual_memory().percent
            stats['swap'] = psutil.swap_memory().percent
        elif self.input_method == 'snmp':
            # Not available
            pass

        # Optionnaly, get the CPU name/frequency
        # thanks to the cpuinfo lib: https://github.com/workhorsy/py-cpuinfo
        if cpuinfo_tag:
            cpu_info = cpuinfo.get_cpu_info()
            #  Check cpu_info (issue #881)
            if cpu_info is not None:
                # Use brand_raw if the key exist (issue #1685)
                if cpu_info.get('brand_raw') is not None:
                    stats['cpu_name'] = cpu_info.get('brand_raw', 'CPU')
                else:
                    stats['cpu_name'] = cpu_info.get('brand', 'CPU')
                if 'hz_actual_raw' in cpu_info:
                    stats['cpu_hz_current'] = cpu_info['hz_actual_raw'][0]
                elif 'hz_actual' in cpu_info:
                    stats['cpu_hz_current'] = cpu_info['hz_actual'][0]
                if 'hz_advertised_raw' in cpu_info:
                    stats['cpu_hz'] = cpu_info['hz_advertised_raw'][0]
                elif 'hz_advertised' in cpu_info:
                    stats['cpu_hz'] = cpu_info['hz_advertised'][0]

        # Update the stats
        self.stats = stats

        return self.stats