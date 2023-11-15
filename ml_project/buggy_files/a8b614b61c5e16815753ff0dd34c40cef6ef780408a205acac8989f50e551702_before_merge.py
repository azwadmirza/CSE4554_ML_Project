    def __init__(self, doc_url, searchindex='searchindex.js',
                 extra_modules_test=None, relative=False):
        self.doc_url = doc_url
        self.relative = relative
        self._link_cache = {}

        self.extra_modules_test = extra_modules_test
        self._page_cache = {}
        if doc_url.startswith('http://'):
            if relative:
                raise ValueError('Relative links are only supported for local '
                                 'URLs (doc_url cannot start with "http://)"')
            searchindex_url = doc_url + '/' + searchindex
        else:
            searchindex_url = os.path.join(doc_url, searchindex)

        # detect if we are using relative links on a Windows system
        if os.name.lower() == 'nt' and not doc_url.startswith('http://'):
            if not relative:
                raise ValueError('You have to use relative=True for the local'
                                 ' package on a Windows system.')
            self._is_windows = True
        else:
            self._is_windows = False

        # download and initialize the search index
        sindex = get_data(searchindex_url)
        filenames, objects = parse_sphinx_searchindex(sindex)

        self._searchindex = dict(filenames=filenames, objects=objects)