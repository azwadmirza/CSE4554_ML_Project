    def handle_folding_range(self, response):
        ranges = response['params']
        folding_panel = self.panels.get(FoldingPanel)
        folding_panel.update_folding(ranges)