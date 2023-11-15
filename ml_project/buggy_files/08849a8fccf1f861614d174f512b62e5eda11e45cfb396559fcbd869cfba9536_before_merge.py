    def has_numeric_only(self, text):
        return bool(re.match(r'(.*)[\s]+(\#NUMERIC_ONLY\#)', text))