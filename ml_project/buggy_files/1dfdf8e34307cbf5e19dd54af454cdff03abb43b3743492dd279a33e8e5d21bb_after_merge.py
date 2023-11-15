    def editor_accepted(self, editor_id):
        data = self._editors[editor_id]
        if not data['readonly']:
            index = data['model'].get_index_from_key(data['key'])
            value = data['editor'].get_value()
            conv_func = data.get('conv', lambda v: v)
            self.set_value(index, conv_func(value))
        # This is needed to avoid the problem reported on
        # issue 8557
        try:
            self._editors.pop(editor_id)
        except KeyError:
            pass
        self.free_memory()