    def editor_rejected(self, editor_id):
        # This is needed to avoid the problem reported on
        # issue 8557
        try:
            self._editors.pop(editor_id)
        except KeyError:
            pass
        self.free_memory()