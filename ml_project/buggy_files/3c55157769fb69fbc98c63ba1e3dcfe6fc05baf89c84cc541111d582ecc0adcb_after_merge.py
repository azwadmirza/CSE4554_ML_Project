    def slug(self):
        if not self.full_slug:
            return None
        return truncate_id(self.full_slug)