    def load_script(self, command, use_reloader=False):
        """
            Loads a script. Returns an error description if something went
            wrong.
        """
        try:
            s = script.Script(command, script.ScriptContext(self))
            s.load()
        except script.ScriptException as e:
            return traceback.format_exc(e)
        if use_reloader:
            script.reloader.watch(s, lambda: self.masterq.put(("script_change", s)))
        self.scripts.append(s)