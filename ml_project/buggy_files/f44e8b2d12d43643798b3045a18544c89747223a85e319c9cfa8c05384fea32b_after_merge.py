    def get_cpu_facts(self):
        i = 0
        vendor_id_occurrence = 0
        model_name_occurrence = 0
        physid = 0
        coreid = 0
        sockets = {}
        cores = {}

        xen = False
        xen_paravirt = False
        try:
            if os.path.exists('/proc/xen'):
                xen = True
            else:
                for line in get_file_lines('/sys/hypervisor/type'):
                    if line.strip() == 'xen':
                        xen = True
                    # Only interested in the first line
                    break
        except IOError:
            pass

        if not os.access("/proc/cpuinfo", os.R_OK):
            return
        self.facts['processor'] = []
        for line in get_file_lines('/proc/cpuinfo'):
            data = line.split(":", 1)
            key = data[0].strip()

            if xen:
                if key == 'flags':
                    # Check for vme cpu flag, Xen paravirt does not expose this.
                    #   Need to detect Xen paravirt because it exposes cpuinfo
                    #   differently than Xen HVM or KVM and causes reporting of
                    #   only a single cpu core.
                    if 'vme' not in data:
                        xen_paravirt = True

            # model name is for Intel arch, Processor (mind the uppercase P)
            # works for some ARM devices, like the Sheevaplug.
            if key in ['model name', 'Processor', 'vendor_id', 'cpu', 'Vendor']:
                if 'processor' not in self.facts:
                    self.facts['processor'] = []
                self.facts['processor'].append(data[1].strip())
                if key == 'vendor_id':
                    vendor_id_occurrence += 1
                if key == 'model name':
                    model_name_occurrence += 1
                i += 1
            elif key == 'physical id':
                physid = data[1].strip()
                if physid not in sockets:
                    sockets[physid] = 1
            elif key == 'core id':
                coreid = data[1].strip()
                if coreid not in sockets:
                    cores[coreid] = 1
            elif key == 'cpu cores':
                sockets[physid] = int(data[1].strip())
            elif key == 'siblings':
                cores[coreid] = int(data[1].strip())
            elif key == '# processors':
                self.facts['processor_cores'] = int(data[1].strip())

        # Skip for platforms without vendor_id/model_name in cpuinfo (e.g ppc64le)
        if vendor_id_occurrence > 0:
            if vendor_id_occurrence == model_name_occurrence:
                i = vendor_id_occurrence

        if self.facts['architecture'] != 's390x':
            if xen_paravirt:
                self.facts['processor_count'] = i
                self.facts['processor_cores'] = i
                self.facts['processor_threads_per_core'] = 1
                self.facts['processor_vcpus'] = i
            else:
                if sockets:
                    self.facts['processor_count'] = len(sockets)
                else:
                    self.facts['processor_count'] = i

                socket_values = list(sockets.values())
                if socket_values and socket_values[0]:
                    self.facts['processor_cores'] = socket_values[0]
                else:
                    self.facts['processor_cores'] = 1

                core_values = list(cores.values())
                if core_values:
                    self.facts['processor_threads_per_core'] = core_values[0] // self.facts['processor_cores']
                else:
                    self.facts['processor_threads_per_core'] = 1 // self.facts['processor_cores']

                self.facts['processor_vcpus'] = (self.facts['processor_threads_per_core'] *
                    self.facts['processor_count'] * self.facts['processor_cores'])