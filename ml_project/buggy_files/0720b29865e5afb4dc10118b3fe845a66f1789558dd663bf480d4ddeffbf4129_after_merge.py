    def apply_domain_edit(self):
        if self.data is not None:
            domain, cols = self.domain_editor.get_domain(self.data.domain, self.data)
            X, y, m = cols
            table = Table.from_numpy(domain, X, y, m, self.data.W)
            table.name = self.data.name
            table.ids = np.array(self.data.ids)
            table.attributes = getattr(self.data, 'attributes', {})
        else:
            table = self.data

        self.send("Data", table)
        self.apply_button.setEnabled(False)