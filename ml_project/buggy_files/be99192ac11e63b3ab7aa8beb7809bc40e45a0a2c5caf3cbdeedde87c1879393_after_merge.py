    def get_cell_as_executable_code(self, cursor=None):
        """Return cell contents as executable code."""
        return self.__exec_cell(cursor)