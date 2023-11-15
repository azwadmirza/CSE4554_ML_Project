    def __call__(self, context, request):
        req_principals = request.effective_principals
        if is_nonstr_iter(req_principals):
            rpset = set(req_principals)
            if self.val.issubset(rpset):
                return True
        return False