        def WORD(self, i=None):
            if i is None:
                return self.getTokens(MetricAlertConditionParser.WORD)
            else:
                return self.getToken(MetricAlertConditionParser.WORD, i)