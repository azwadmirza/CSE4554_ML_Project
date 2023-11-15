    def _paginate(self, data=None, data_generator=None, sort=None):
        try:
            arg_page = self._get_page()
            arg_limit = self._get_limit()
        except HTTPError as error:
            return self._bad_request(error.message)

        headers = {
            'X-Pagination-Page': arg_page,
            'X-Pagination-Limit': arg_limit
        }

        first_page = arg_page if arg_page > 0 else 1
        previous_page = None if arg_page <= 1 else arg_page - 1
        if data_generator:
            results = list(data_generator())[:arg_limit]
            next_page = None if len(results) < arg_limit else arg_page + 1
            last_page = None
        else:
            arg_sort = self._get_sort(default=sort)
            start = (arg_page - 1) * arg_limit
            end = start + arg_limit
            results = data
            if arg_sort:
                # Compare to earliest datetime instead of None
                def safe_compare(field, results):
                    if field == 'airDate' and results[field] is None:
                        return text_type(datetime.min)
                    return results[field]

                try:
                    for field, reverse in reversed(arg_sort):
                        results = sorted(results, key=partial(safe_compare, field), reverse=reverse)
                except KeyError:
                    return self._bad_request('Invalid sort query parameter')

            count = len(results)
            headers['X-Pagination-Count'] = count
            results = results[start:end]
            next_page = None if end > count else arg_page + 1
            last_page = ((count - 1) // arg_limit) + 1
            headers['X-Pagination-Total'] = last_page
            if last_page <= arg_page:
                last_page = None

        # Reconstruct the query parameters
        query_params = []
        for arg, values in viewitems(self.request.query_arguments):
            if arg in ('page', 'limit'):
                continue
            if not isinstance(values, list):
                values = [values]
            query_params += [(arg, value) for value in values]

        bare_uri = url_concat(self.request.path, query_params)

        links = []
        for rel, page in (('next', next_page), ('last', last_page),
                          ('first', first_page), ('previous', previous_page)):
            if page is None:
                continue

            uri = url_concat(bare_uri, dict(page=page, limit=arg_limit))
            link = '<{uri}>; rel="{rel}"'.format(uri=uri, rel=rel)
            links.append(link)

        self.set_header('Link', ', '.join(links))

        return self._ok(data=results, headers=headers)