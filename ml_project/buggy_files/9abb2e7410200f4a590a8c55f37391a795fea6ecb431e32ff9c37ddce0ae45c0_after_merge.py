    def _set_data(self, new_data):
        """Note this setter will be called by the
            `super(BaseQueryCompiler).__init__` function
        """
        raise NotImplementedError("Must be implemented in children classes")