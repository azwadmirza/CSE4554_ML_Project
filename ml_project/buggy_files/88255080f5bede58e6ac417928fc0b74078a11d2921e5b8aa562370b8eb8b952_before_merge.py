    def verify(self):
        validation_error = super(PrefixReplaceLinkAction, self).verify()
        if validation_error:
            return validation_error

        if islink(self.source_full_path):
            log.trace("ignoring prefix update for symlink with source path %s",
                      self.source_full_path)
            # return
            assert False, "I don't think this is the right place to ignore this"

        self.intermediate_path = join(self.transaction_context['temp_dir'], text_type(uuid4()))

        log.trace("copying %s => %s", self.source_full_path, self.intermediate_path)
        create_link(self.source_full_path, self.intermediate_path, LinkType.copy)

        try:
            log.trace("rewriting prefixes in %s", self.target_full_path)
            update_prefix(self.intermediate_path,
                          context.target_prefix_override or self.target_prefix,
                          self.prefix_placeholder,
                          self.file_mode)
        except _PaddingError:
            raise PaddingError(self.target_full_path, self.prefix_placeholder,
                               len(self.prefix_placeholder))

        sha256_in_prefix = compute_sha256sum(self.intermediate_path)

        self.prefix_path_data = PathDataV1.from_objects(
            self.prefix_path_data,
            file_mode=self.file_mode,
            path_type=PathType.hardlink,
            prefix_placeholder=self.prefix_placeholder,
            sha256_in_prefix=sha256_in_prefix,
        )

        self._verified = True