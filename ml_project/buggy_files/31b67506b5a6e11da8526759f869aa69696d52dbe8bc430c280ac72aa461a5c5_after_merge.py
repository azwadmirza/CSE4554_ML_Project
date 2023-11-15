    def run_script_once(self, command, f):
        sc = self.addons.get("scriptloader")
        try:
            with self.handlecontext():
                sc.run_once(command, [f])
        except mitmproxy.exceptions.AddonError as e:
            signals.add_log("Script error: %s" % e, "warn")