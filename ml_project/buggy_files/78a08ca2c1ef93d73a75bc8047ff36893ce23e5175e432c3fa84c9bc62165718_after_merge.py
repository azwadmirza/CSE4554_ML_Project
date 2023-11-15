    def _read_utilization(self):
        with self.lock:
            if psutil is not None:
                self.values["cpu_util_percent"].append(
                    float(psutil.cpu_percent(interval=None)))
                self.values["ram_util_percent"].append(
                    float(getattr(psutil.virtual_memory(), "percent")))
            if GPUtil is not None:
                gpu_list = []
                try:
                    gpu_list = GPUtil.getGPUs()
                except Exception:
                    logger.debug("GPUtil failed to retrieve GPUs.")
                for gpu in gpu_list:
                    self.values["gpu_util_percent" + str(gpu.id)].append(
                        float(gpu.load))
                    self.values["vram_util_percent" + str(gpu.id)].append(
                        float(gpu.memoryUtil))