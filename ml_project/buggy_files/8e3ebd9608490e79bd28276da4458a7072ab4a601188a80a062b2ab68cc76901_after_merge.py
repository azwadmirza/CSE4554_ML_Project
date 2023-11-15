    def _js_call(self, command, callback=None):
        self._tab.run_js_async(javascript.assemble('caret', command), callback)