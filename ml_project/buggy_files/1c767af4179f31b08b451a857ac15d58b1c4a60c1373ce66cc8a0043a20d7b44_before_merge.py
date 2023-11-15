    def cleanup(self):
        super().cleanup()
        self._save_marker_cache()

        for proxy in self.export_proxies:
            proxy.cancel()
            self.export_proxies.remove(proxy)