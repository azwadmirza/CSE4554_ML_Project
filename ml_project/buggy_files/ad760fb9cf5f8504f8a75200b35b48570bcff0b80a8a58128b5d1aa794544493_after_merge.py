    def write(self, string):
        self.__assert_not_frozen('write')
        self.__check_capacity(len(string))
        assert isinstance(string, hbytes)
        original = self.index
        self.__write(string)
        self.forced_indices.update(hrange(original, self.index))
        self.forced_blocks.add(len(self.blocks) - 1)
        return string