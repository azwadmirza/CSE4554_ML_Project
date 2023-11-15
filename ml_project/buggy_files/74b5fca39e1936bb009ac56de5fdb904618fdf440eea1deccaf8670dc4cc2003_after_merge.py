    def run_once(self, command, flows):
        try:
            sc = Script(command)
        except ValueError as e:
            raise ValueError(str(e))
        sc.load_script()
        for f in flows:
            for evt, o in events.event_sequence(f):
                sc.run(evt, o)
        sc.done()
        return sc