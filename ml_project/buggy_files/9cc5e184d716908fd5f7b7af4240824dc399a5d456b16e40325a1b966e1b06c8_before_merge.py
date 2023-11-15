    def __setstate__(self, d):
        self.__dict__ = d

        # reload tokenizer to get around serialization issues
        model_name = self.name.split('transformer-word-')[-1]
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        except:
            pass