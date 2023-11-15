    def analyze_content(self):
        if self._content_was_analyzed:
            return

        self._content_was_analyzed = True

        if self.is_compact_ast:
            body = self._functionNotParsed['body']

            if body and body[self.get_key()] == 'Block':
                self._is_implemented = True
                self._parse_cfg(body)

            for modifier in self._functionNotParsed['modifiers']:
                self._parse_modifier(modifier)

        else:
            children = self._functionNotParsed[self.get_children('children')]
            self._is_implemented = False
            for child in children[2:]:
                if child[self.get_key()] == 'Block':
                    self._is_implemented = True
                    self._parse_cfg(child)
    
            # Parse modifier after parsing all the block
            # In the case a local variable is used in the modifier
            for child in children[2:]:
                if child[self.get_key()] == 'ModifierInvocation':
                    self._parse_modifier(child)

        for local_vars in self.variables:
            local_vars.analyze(self)

        for node in self.nodes:
            node.analyze_expressions(self)

        self._filter_ternary()
        self._remove_alone_endif()