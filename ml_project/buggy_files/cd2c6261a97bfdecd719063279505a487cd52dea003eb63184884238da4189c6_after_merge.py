    def episode(self):
        if self.id_type == 'ep':
            return self.id[1]
        if self.id_type == 'sequence':
            return self.id
        return None