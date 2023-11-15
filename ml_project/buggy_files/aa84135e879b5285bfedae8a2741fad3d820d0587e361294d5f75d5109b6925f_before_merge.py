    def handle_show_map(self, args):
        print("Region          Start         End                 Size    Access    Blocksize")
        for region in self.target.get_memory_map():
            print("{:<15} {:#010x}    {:#010x}    {:#10x}    {:<9} {}".format(
                region.name,
                region.start,
                region.end,
                region.length,
                region.access,
                region.blocksize if region.is_flash else '-'))