    def get(self, request, *args, **kwargs):
        # Fetch the category; return 404 or redirect as needed
        self.category = self.get_category()
        redirect = self.redirect_if_necessary(request.path, self.category)
        if redirect is not None:
            return redirect

        self.search_handler = self.get_search_handler(
            request.GET, request.get_full_path(), self.get_categories())

        return super(ProductCategoryView, self).get(request, *args, **kwargs)