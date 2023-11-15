    def __getstate__(self):
        state = self.__dict__.copy()
        state["tokenizer"] = None
        return state