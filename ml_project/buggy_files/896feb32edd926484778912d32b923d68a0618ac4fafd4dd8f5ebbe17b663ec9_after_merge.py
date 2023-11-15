    def yank(self, what='url', sel=False, keep=False):
        """Yank something to the clipboard or primary selection.

        Args:
            what: What to yank.

                - `url`: The current URL.
                - `pretty-url`: The URL in pretty decoded form.
                - `title`: The current page's title.
                - `domain`: The current scheme, domain, and port number.
                - `selection`: The selection under the cursor.

            sel: Use the primary selection instead of the clipboard.
            keep: Stay in visual mode after yanking the selection.
        """
        if what == 'title':
            s = self._tabbed_browser.widget.page_title(self._current_index())
        elif what == 'domain':
            port = self._current_url().port()
            s = '{}://{}{}'.format(self._current_url().scheme(),
                                   self._current_url().host(),
                                   ':' + str(port) if port > -1 else '')
        elif what in ['url', 'pretty-url']:
            s = self._yank_url(what)
            what = 'URL'  # For printing
        elif what == 'selection':
            def _selection_callback(s):
                if not s:
                    message.info("Nothing to yank")
                    return
                self._yank_to_target(s, sel, what, keep)

            caret = self._current_widget().caret
            caret.selection(callback=_selection_callback)
            return
        else:  # pragma: no cover
            raise ValueError("Invalid value {!r} for `what'.".format(what))

        self._yank_to_target(s, sel, what, keep)