    def fillna(self, value, inplace=False):
        new_values = self.values if inplace else self.values.copy()

        mask = com.isnull(new_values)
        np.putmask(new_values, mask, value)

        if inplace:
            return self
        else:
            return make_block(new_values, self.items, self.ref_items)