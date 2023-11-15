    def extract_blocks(self, source_file: FileBlock) -> Iterable[BlockTag]:
        try:
            blocks = extract_toplevel_blocks(
                source_file.contents,
                allowed_blocks=self.allowed_blocks,
                collect_raw_data=False
            )
            # this makes mypy happy, and this is an invariant we really need
            for block in blocks:
                assert isinstance(block, BlockTag)
                yield block

        except CompilationException as exc:
            if exc.node is None:
                # TODO(jeb): attach info about resource type/file path here
                exc.node = NotImplemented
            raise