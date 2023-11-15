        def selection(self, new_content: str):
            Gdk.threads_enter()
            try:
                # This call might fail and raise an Exception.
                # If it does, make sure to release the mutex and not deadlock AutoKey.
                self._selection.set_text(new_content, -1)
            finally:
                Gdk.threads_leave()