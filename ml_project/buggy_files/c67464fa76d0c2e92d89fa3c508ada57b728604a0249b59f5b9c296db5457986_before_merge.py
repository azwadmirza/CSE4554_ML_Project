    def find_blocks(self, allowed_blocks=None, collect_raw_data=True):
        """Find all top-level blocks in the data."""
        if allowed_blocks is None:
            allowed_blocks = {'snapshot', 'macro', 'materialization', 'docs'}

        for tag in self.tag_parser.find_tags():
            if tag.block_type_name in _CONTROL_FLOW_TAGS:
                self.stack.append(tag.block_type_name)
            elif tag.block_type_name in _CONTROL_FLOW_END_TAGS:
                found = None
                if self.stack:
                    found = self.stack.pop()
                else:
                    expected = _CONTROL_FLOW_END_TAGS[tag.block_type_name]
                    dbt.exceptions.raise_compiler_error((
                        'Got an unexpected control flow end tag, got {} but '
                        'never saw a preceeding {} (@ {})'
                    ).format(tag.block_type_name, expected, tag.start))
                expected = _CONTROL_FLOW_TAGS[found]
                if expected != tag.block_type_name:
                    dbt.exceptions.raise_compiler_error((
                        'Got an unexpected control flow end tag, got {} but '
                        'expected {} next (@ {})'
                    ).format(tag.block_type_name, expected, tag.start))

            if tag.block_type_name in allowed_blocks:
                if self.stack:
                    dbt.exceptions.raise_compiler_error((
                        'Got a block definition inside control flow at {}. '
                        'All dbt block definitions must be at the top level'
                    ).format(tag.start))
                if self.current is not None:
                    dbt.exceptions.raise_compiler_error(
                        duplicate_tags.format(outer=self.current, inner=tag)
                    )
                if collect_raw_data:
                    raw_data = self.data[self.last_position:tag.start]
                    self.last_position = tag.start
                    if raw_data:
                        yield BlockData(raw_data)
                self.current = tag

            elif self.is_current_end(tag):
                self.last_position = tag.end
                yield BlockTag(
                    block_type_name=self.current.block_type_name,
                    block_name=self.current.block_name,
                    contents=self.data[self.current.end:tag.start],
                    full_block=self.data[self.current.start:tag.end]
                )
                self.current = None

        if self.current:
            dbt.exceptions.raise_compiler_error((
                'Reached EOF without finding a close block for '
                '{0.block_type_name} (from {0.end})'
            ).format(self.current))

        if collect_raw_data:
            raw_data = self.data[self.last_position:]
            if raw_data:
                yield BlockData(raw_data)