    def _inject_userjs(self, frame):
        """Inject user JavaScripts into the page.

        Args:
            frame: The QWebFrame to inject the user scripts into.
        """
        if sip.isdeleted(frame):
            log.greasemonkey.debug("_inject_userjs called for deleted frame!")
            return

        url = frame.url()
        if url.isEmpty():
            url = frame.requestedUrl()

        log.greasemonkey.debug("_inject_userjs called for {} ({})"
                               .format(frame, url.toDisplayString()))

        greasemonkey = objreg.get('greasemonkey')
        scripts = greasemonkey.scripts_for(url)
        # QtWebKit has trouble providing us with signals representing
        # page load progress at reasonable times, so we just load all
        # scripts on the same event.
        toload = scripts.start + scripts.end + scripts.idle

        if url.isEmpty():
            # This happens during normal usage like with view source but may
            # also indicate a bug.
            log.greasemonkey.debug("Not running scripts for frame with no "
                                   "url: {}".format(frame))
            assert not toload, toload

        for script in toload:
            if frame is self.mainFrame() or script.runs_on_sub_frames:
                log.webview.debug('Running GM script: {}'.format(script.name))
                frame.evaluateJavaScript(script.code())