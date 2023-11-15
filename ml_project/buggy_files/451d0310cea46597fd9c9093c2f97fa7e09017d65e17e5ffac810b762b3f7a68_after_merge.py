    def visit_file(self, file_node: MypyFile, path: str, options: Options) -> None:
        """Type check a mypy file with the given path."""
        self.options = options
        self.pass_num = 0
        self.is_stub = file_node.is_stub
        self.errors.set_file(path)
        self.globals = file_node.names
        self.enter_partial_types()
        self.is_typeshed_stub = self.errors.is_typeshed_file(path)
        self.module_type_map = {}
        self.module_refs = set()
        if self.options.strict_optional_whitelist is None:
            self.suppress_none_errors = not self.options.show_none_errors
        else:
            self.suppress_none_errors = not any(fnmatch.fnmatch(path, pattern)
                                                for pattern
                                                in self.options.strict_optional_whitelist)

        with self.binder.top_frame_context():
            for d in file_node.defs:
                self.accept(d)

        self.leave_partial_types()

        if self.deferred_nodes:
            self.check_second_pass()

        self.current_node_deferred = False

        all_ = self.globals.get('__all__')
        if all_ is not None and all_.type is not None:
            seq_str = self.named_generic_type('typing.Sequence',
                                              [self.named_type('builtins.str')])
            if not is_subtype(all_.type, seq_str):
                str_seq_s, all_s = self.msg.format_distinctly(seq_str, all_.type)
                self.fail(messages.ALL_MUST_BE_SEQ_STR.format(str_seq_s, all_s),
                          all_.node)

        del self.options