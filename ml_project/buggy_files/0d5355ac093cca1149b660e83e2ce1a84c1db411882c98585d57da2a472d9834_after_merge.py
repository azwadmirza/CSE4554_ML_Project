    def cpu_affinity_set(self, cpus):
        try:
            cext.proc_cpu_affinity_set(self.pid, cpus)
        except (OSError, ValueError) as err:
            if isinstance(err, ValueError) or err.errno == errno.EINVAL:
                allcpus = tuple(range(len(per_cpu_times())))
                for cpu in cpus:
                    if cpu not in allcpus:
                        raise ValueError(
                            "invalid CPU number %r; choose between %s" % (
                                cpu, allcpus))
            raise