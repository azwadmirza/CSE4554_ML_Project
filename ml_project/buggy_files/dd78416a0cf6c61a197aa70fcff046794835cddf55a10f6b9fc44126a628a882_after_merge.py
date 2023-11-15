    def get_value(self, result):
        try:
            return self.get_json(result)
        except (IndexError, TypeError, AttributeError):
            msg = 'unable to apply conditional to result'
            raise FailedConditionalError(msg, self.raw)