    def add_route(self, method, path, handler, *, name=None):
        assert path.startswith('/')
        assert callable(handler), handler
        if not asyncio.iscoroutinefunction(handler):
            handler = asyncio.coroutine(handler)
        method = method.upper()
        assert method in self.METHODS, method
        parts = []
        factory = PlainRoute
        format_parts = []
        for part in path.split('/'):
            if not part:
                continue
            match = self.DYN.match(part)
            if match:
                parts.append('(?P<' + match.group('var') + '>' +
                             self.GOOD + ')')
                factory = DynamicRoute
                format_parts.append('{'+match.group('var')+'}')
                continue

            match = self.DYN_WITH_RE.match(part)
            if match:
                parts.append('(?P<' + match.group('var') + '>' +
                             match.group('re') + ')')
                factory = DynamicRoute
                format_parts.append('{'+match.group('var')+'}')
                continue
            if self.PLAIN.match(part):
                parts.append(re.escape(part))
                format_parts.append(part)
                continue
            raise ValueError("Invalid path '{}'['{}']".format(path, part))
        if factory is PlainRoute:
            route = PlainRoute(method, handler, name, path)
        else:
            pattern = '/' + '/'.join(parts)
            if path.endswith('/') and pattern != '/':
                pattern += '/'
            try:
                compiled = re.compile('^' + pattern + '$')
            except re.error as exc:
                raise ValueError(
                    "Bad pattern '{}': {}".format(pattern, exc)) from None
            formatter = '/' + '/'.join(format_parts)
            route = DynamicRoute(method, handler, name, compiled, formatter)
        self._register_endpoint(route)
        return route