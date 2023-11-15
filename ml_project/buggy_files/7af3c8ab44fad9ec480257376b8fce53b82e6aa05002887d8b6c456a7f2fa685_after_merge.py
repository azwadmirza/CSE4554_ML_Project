    def __call__(self, context, request):
        result = self.predicate(context, request)
        phash = self.phash()
        if phash:
            result = not result
        return result