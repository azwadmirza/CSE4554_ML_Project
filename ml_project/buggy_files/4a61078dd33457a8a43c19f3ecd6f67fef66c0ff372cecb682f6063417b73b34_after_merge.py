    def handle_compare(self, args):
        if len(args) < 2:
            print("Error: missing argument")
            return 1
        addr = self.convert_value(args[0])
        if len(args) < 3:
            filename = args[1]
            length = None
        else:
            filename = args[2]
            length = self.convert_value(args[1])

        region = self.session.target.memory_map.get_region_for_address(addr)
        flash_init_required =  region is not None and region.is_flash and not region.is_powered_on_boot and region.flash is not None
        if flash_init_required:
            try:
                region.flash.init(region.flash.Operation.VERIFY)
            except exceptions.FlashFailure:
                region.flash.init(region.flash.Operation.ERASE)

        with open(filename, 'rb') as f:
            file_data = f.read(length)
        
        if length is None:
            length = len(file_data)
        elif len(file_data) < length:
            print("File is %d bytes long; reducing comparison length to match." % len(file_data))
            length = len(file_data)
        
        # Divide into 32 kB chunks.
        CHUNK_SIZE = 32 * 1024
        chunk_count = (length + CHUNK_SIZE - 1) // CHUNK_SIZE
        
        end_addr = addr + length
        offset = 0
        mismatch = False
        
        for chunk in range(chunk_count):
            # Get this chunk's size.
            chunk_size = min(end_addr - addr, CHUNK_SIZE)
            print("Comparing %d bytes @ 0x%08x" % (chunk_size, addr))
            
            data = bytearray(self.target.aps[self.selected_ap].read_memory_block8(addr, chunk_size))
            
            for i in range(chunk_size):
                if data[i] != file_data[offset+i]:
                    mismatch = True
                    print("Mismatched byte at 0x%08x (offset 0x%x): 0x%02x (memory) != 0x%02x (file)" %
                        (addr + i, offset + i, data[i], file_data[offset+i]))
                    break
        
            if mismatch:
                break
        
            offset += chunk_size
            addr += chunk_size
        
        if not mismatch:
            print("All %d bytes match." % length)

        if flash_init_required:
            region.flash.cleanup()