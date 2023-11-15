    def __getstate__(self):
        state = self.__dict__.copy()
        state["value"] = self.value
        del state["_value_buffer"]
        return state