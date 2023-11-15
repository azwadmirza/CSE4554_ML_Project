    def handle_show_map(self, args):
        pt = prettytable.PrettyTable(["Region", "Start", "End", "Size", "Access", "Sector", "Page"])
        pt.align = 'l'
        pt.border = False
        for region in self.target.get_memory_map():
            pt.add_row([
                region.name,
                "0x%08x" % region.start,
                "0x%08x" % region.end,
                "0x%08x" % region.length,
                region.access,
                ("0x%08x" % region.sector_size) if region.is_flash else '-',
                ("0x%08x" % region.page_size) if region.is_flash else '-',
                ])
        print(pt)