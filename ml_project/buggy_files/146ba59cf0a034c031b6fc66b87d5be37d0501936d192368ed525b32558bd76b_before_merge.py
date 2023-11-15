    def entity_zero_or_selectable(self):
        if self.entity_zero is not None:
            return self.entity_zero
        elif self.actual_froms:
            return list(self.actual_froms)[0]
        else:
            return None