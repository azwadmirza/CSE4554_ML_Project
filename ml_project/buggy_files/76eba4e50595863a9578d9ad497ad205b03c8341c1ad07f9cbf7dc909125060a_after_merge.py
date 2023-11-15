    def evaluate_js(self, script):
        def _evaluate_js():
            self.webview.execute_script(code)
            result_semaphore.release()

        self.eval_js_lock.acquire()
        result_semaphore = Semaphore(0)
        self.js_result_semaphores.append(result_semaphore)
        # Backup the doc title and store the result in it with a custom prefix
        unique_id = uuid1().hex
        code = 'window.oldTitle{0} = document.title; document.title = {1};'.format(unique_id, script)

        self.load_event.wait()
        glib.idle_add(_evaluate_js)
        result_semaphore.acquire()

        if not gtk.main_level():
            # Webview has been closed, don't proceed
            return None

        result = self.webview.get_title()
        result = None if result == 'undefined' or result == 'null' or result is None else result if result == '' else json.loads(result)

        # Restore document title and return
        code = 'document.title = window.oldTitle{0}'.format(unique_id)
        glib.idle_add(_evaluate_js)
        self.js_result_semaphores.remove(result_semaphore)
        self.eval_js_lock.release()

        return result