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

        try:
            self.qemu.stop_backend()
        except libvirt.libvirtError:
            print('Not connected to Qemu')