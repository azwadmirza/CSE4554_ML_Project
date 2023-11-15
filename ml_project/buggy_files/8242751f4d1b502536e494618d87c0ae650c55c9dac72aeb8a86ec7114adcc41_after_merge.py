    def analyze_content(self):
        if self._content_was_analyzed:
            return

        self._content_was_analyzed = True


        if self.is_compact_ast:
            body = self._functionNotParsed['body']

            if body and body[self.get_key()] == 'Block':
                self._is_implemented = True
                self._parse_cfg(body)

        else:
            children = self._functionNotParsed['children']

            self._isImplemented = False
            if len(children) > 1:
                assert len(children) == 2
                block = children[1]
                assert block['name'] == 'Block'
                self._is_implemented = True
                self._parse_cfg(block)

        for local_vars in self.variables:
            local_vars.analyze(self)

        for node in self.nodes:
            node.analyze_expressions(self)

        self._filter_ternary()
        self._remove_alone_endif()

        self._analyze_read_write()
        self._analyze_calls()