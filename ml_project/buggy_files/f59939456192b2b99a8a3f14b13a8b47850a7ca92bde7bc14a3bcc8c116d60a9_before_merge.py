    def editor_rejected(self, editor_id):
        self._editors.pop(editor_id)
        self.free_memory()