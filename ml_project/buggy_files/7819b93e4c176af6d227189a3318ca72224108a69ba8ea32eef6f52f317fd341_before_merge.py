    def get(self, request, *args, **kwargs):
        order = request.GET.get('order', '')
        if not ((not order.startswith('-') or order.count('-') == 1) and (order.lstrip('-') in self.all_sorts)):
            order = self.get_default_sort_order(request)
        self.order = order

        return super(QueryStringSortMixin, self).get(request, *args, **kwargs)