    def _init_js(self):
        js_code = '\n'.join([
            '"use strict";',
            'window._qutebrowser = window._qutebrowser || {};',
            utils.read_file('javascript/scroll.js'),
            utils.read_file('javascript/webelem.js'),
            utils.read_file('javascript/caret.js'),
        ])
        script = QWebEngineScript()
        # We can't use DocumentCreation here as WORKAROUND for
        # https://bugreports.qt.io/browse/QTBUG-66011
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setSourceCode(js_code)

        page = self._widget.page()
        script.setWorldId(QWebEngineScript.ApplicationWorld)

        # FIXME:qtwebengine  what about runsOnSubFrames?
        page.scripts().insert(script)