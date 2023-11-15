    def _js_call(self, command):
        self._tab.run_js_async(
            javascript.assemble('caret', command))