    def _init_js(self):
        """Initialize global qutebrowser JavaScript."""
        js_code = javascript.wrap_global(
            'scripts',
            utils.read_file('javascript/scroll.js'),
            utils.read_file('javascript/webelem.js'),
            utils.read_file('javascript/caret.js'),
        )
        # FIXME:qtwebengine what about subframes=True?
        self._inject_early_js('js', js_code, subframes=True)
        self._init_stylesheet()

        greasemonkey = objreg.get('greasemonkey')
        greasemonkey.scripts_reloaded.connect(self._inject_userscripts)
        self._inject_userscripts()