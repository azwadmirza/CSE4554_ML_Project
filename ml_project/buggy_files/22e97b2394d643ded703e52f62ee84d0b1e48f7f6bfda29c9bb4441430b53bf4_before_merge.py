    def get(self, request, *args, **kwargs):
        self.search_handler = self.get_search_handler(
            self.request.GET, request.get_full_path(), [])
        return super(CatalogueView, self).get(request, *args, **kwargs)