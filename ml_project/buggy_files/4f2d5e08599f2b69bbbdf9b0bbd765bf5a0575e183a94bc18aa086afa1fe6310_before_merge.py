        def selection(self, new_content: str):
            Gdk.threads_enter()
            self._selection.set_text(new_content, -1)
            Gdk.threads_leave()