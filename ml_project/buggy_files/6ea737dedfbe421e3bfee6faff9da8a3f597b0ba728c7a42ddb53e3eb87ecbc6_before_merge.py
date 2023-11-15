    def fillna(self, value, inplace=False):
        """

        """
        new_blocks = [b.fillna(value, inplace=inplace)
                      if b._can_hold_na else b
                      for b in self.blocks]
        if inplace:
            return self
        return BlockManager(new_blocks, self.axes)