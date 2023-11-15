    def import_object(self, raiseerror: bool = False) -> bool:
        """Never import anything."""
        # disguise as an attribute
        self.objtype = 'attribute'
        self._datadescriptor = True

        with mock(self.env.config.autodoc_mock_imports):
            try:
                ret = import_object(self.modname, self.objpath[:-1], 'class',
                                    attrgetter=self.get_attr,
                                    warningiserror=self.env.config.autodoc_warningiserror)
                self.module, _, _, self.parent = ret
                return True
            except ImportError as exc:
                if raiseerror:
                    raise
                else:
                    logger.warning(exc.args[0], type='autodoc', subtype='import_object')
                    self.env.note_reread()
                    return False