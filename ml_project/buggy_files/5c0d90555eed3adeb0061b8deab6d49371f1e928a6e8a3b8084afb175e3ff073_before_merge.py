    def flash_op(self, data):
        ops = data.split(b':')[0]
        LOG.debug("flash op: %s", ops)

        if ops == b'FlashErase':
            return self.create_rsp_packet(b"OK")

        elif ops == b'FlashWrite':
            write_addr = int(data.split(b':')[1], 16)
            LOG.debug("flash write addr: 0x%x", write_addr)
            # search for second ':' (beginning of data encoded in the message)
            second_colon = 0
            idx_begin = 0
            while second_colon != 2:
                if data[idx_begin:idx_begin+1] == b':':
                    second_colon += 1
                idx_begin += 1

            # Get flash loader if there isn't one already
            if self.flash_loader is None:
                self.flash_loader = FlashLoader(self.session)

            # Add data to flash loader
            self.flash_loader.add_data(write_addr, unescape(data[idx_begin:len(data) - 3]))

            return self.create_rsp_packet(b"OK")

        # we need to flash everything
        elif b'FlashDone' in ops :
            # Only program if we received data.
            if self.flash_loader is not None:
                # Write all buffered flash contents.
                self.flash_loader.commit()

                # Set flash loader to None so that on the next flash command a new
                # object is used.
                self.flash_loader = None

            self.first_run_after_reset_or_flash = True
            if self.thread_provider is not None:
                self.thread_provider.read_from_target = False

            return self.create_rsp_packet(b"OK")

        return None