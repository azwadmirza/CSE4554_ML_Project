    def _on_table_create(self, target, bind, checkfirst=False, **kw):

        if (
            checkfirst
            or (
                not self.metadata
                and not kw.get("_is_metadata_operation", False)
            )
        ) and not self._check_for_name_in_memos(checkfirst, kw):
            self.create(bind=bind, checkfirst=checkfirst)