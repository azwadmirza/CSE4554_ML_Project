    def nsmallest(self, *args, **kwargs):
        return self.nsort(sort_type="nsmallest", *args, **kwargs)