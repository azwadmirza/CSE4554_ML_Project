    def stop_pool(self):
        # lazy import to avoid exception if not using the backend_pool and libvirt not installed (#1185)
        import libvirt

        log.msg(eventid='cowrie.backend_pool.service',
                format='Trying pool clean stop')

        # stop loop
        if self.loop_next_call:
            self.loop_next_call.cancel()

        # try destroying all guests
        for guest in self.guests:
            self.qemu.destroy_guest(guest['domain'], guest['snapshot'])

        # force destroy remaining stuff
        self.qemu.destroy_all_cowrie()

        # close any NAT sockets
        if not self.local_pool and self.use_nat or self.pool_only:
            log.msg(eventid='cowrie.backend_pool.service', format='Free all NAT bindings')
            self.nat_service.free_all()

        try:
            self.qemu.stop_backend()
        except libvirt.libvirtError:
            print('Not connected to Qemu')