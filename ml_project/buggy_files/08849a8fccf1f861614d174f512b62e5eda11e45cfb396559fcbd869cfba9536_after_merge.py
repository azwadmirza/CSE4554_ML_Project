    def has_numeric_only(self, text):
        return bool(re.search(r'(.*)[\s]+(\#NUMERIC_ONLY\#)', text))