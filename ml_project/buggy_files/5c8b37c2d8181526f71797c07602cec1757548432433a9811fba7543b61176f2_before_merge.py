        def hide(self):
            J.execute_runnable_in_main_thread(J.run_script("""
            new java.lang.Runnable() {
            run: function() { o.hide(); }}""", dict(o, self.o)), synchronous=True)