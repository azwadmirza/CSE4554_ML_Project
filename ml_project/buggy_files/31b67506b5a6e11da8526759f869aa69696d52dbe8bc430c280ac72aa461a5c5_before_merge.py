    def run_script_once(self, command, f):
        if not command:
            return
        signals.add_log("Running script on flow: %s" % command, "debug")

        try:
            s = script.Script(command)
            s.load()
        except script.ScriptException as e:
            signals.status_message.send(
                message='Error loading "{}".'.format(command)
            )
            signals.add_log('Error loading "{}":\n{}'.format(command, e), "error")
            return

        if f.request:
            self._run_script_method("request", s, f)
        if f.response:
            self._run_script_method("response", s, f)
        if f.error:
            self._run_script_method("error", s, f)
        s.unload()
        signals.flow_change.send(self, flow = f)