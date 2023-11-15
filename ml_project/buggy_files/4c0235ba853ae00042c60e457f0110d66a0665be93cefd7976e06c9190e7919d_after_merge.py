    def season(self):
        if self.id_type == 'ep':
            return self.id[0]
        if self.id_type == 'date':
            return self.id.year
        if self.id_type == 'sequence':
            return 0
        return None