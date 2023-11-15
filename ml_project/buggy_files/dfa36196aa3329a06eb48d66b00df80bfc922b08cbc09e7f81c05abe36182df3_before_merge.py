    def start(self):
        if not self.use_upnp:
            self.external_ip = CS.get_external_ip()
            return
        success = False
        yield self._maintain_redirects()
        if self.upnp:
            if not self.upnp_redirects:
                log.error("failed to setup upnp, debugging infomation: %s", self.upnp.zipped_debugging_info)
            else:
                success = True
                log.debug("set up upnp port redirects for gateway: %s", self.upnp.gateway.manufacturer_string)
        else:
            log.error("failed to setup upnp")
        self.component_manager.analytics_manager.send_upnp_setup_success_fail(success, self.get_status())
        self._maintain_redirects_lc.start(360, now=False)