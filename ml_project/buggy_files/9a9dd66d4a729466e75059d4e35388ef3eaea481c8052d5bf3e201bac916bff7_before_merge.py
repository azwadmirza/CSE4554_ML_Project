    def cpu_freq():
        """Alternate implementation using /proc/cpuinfo.
        min and max frequencies are not available and are set to None.
        """
        ret = []
        with open_binary('%s/cpuinfo' % get_procfs_path()) as f:
            for line in f:
                if line.lower().startswith(b'cpu mhz'):
                    key, value = line.split(b'\t:', 1)
                    ret.append(_common.scpufreq(float(value), None, None))
        return ret