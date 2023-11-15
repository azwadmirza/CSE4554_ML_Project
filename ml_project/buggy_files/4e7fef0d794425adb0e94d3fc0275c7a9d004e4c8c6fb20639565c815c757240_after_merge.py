    def __str__(self):
        s = "s" if self.ghost_zones != 1 else ""
        return f"fields {self.fields} require {self.ghost_zones} ghost zone{s}."