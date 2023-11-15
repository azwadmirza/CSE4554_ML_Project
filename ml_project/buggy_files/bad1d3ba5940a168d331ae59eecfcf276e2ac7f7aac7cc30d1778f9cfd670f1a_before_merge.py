    def handle_savemem(self, args):
        if len(args) < 3:
            print("Error: missing argument")
            return 1
        addr = self.convert_value(args[0])
        count = self.convert_value(args[1])
        filename = args[2]

        region = self.session.target.memory_map.get_region_for_address(addr)
        flash_init_required =  region is not None and region.is_flash and not region.is_powered_on_boot and region.flash is not None
        if flash_init_required:
            region.flash.init(region.flash.Operation.VERIFY)

        data = bytearray(self.target.aps[self.selected_ap].read_memory_block8(addr, count))

        if flash_init_required:
            region.flash.cleanup()

        with open(filename, 'wb') as f:
            f.write(data)
            print("Saved %d bytes to %s" % (count, filename))