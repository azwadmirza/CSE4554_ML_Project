    def keypress(self, xxx_todo_changeme, key):
        (maxcol,) = xxx_todo_changeme
        key = common.shortcuts(key)
        if key == "a":
            self.flow.resume(self.master)
            signals.flowlist_change.send(self)
        elif key == "d":
            if self.flow.killable:
                self.flow.kill(self.master)
            self.master.view.remove(self.master.view.focus.flow)
        elif key == "D":
            cp = self.flow.copy()
            self.master.view.add(cp)
            self.master.view.focus.flow = cp
        elif key == "m":
            self.flow.marked = not self.flow.marked
            signals.flowlist_change.send(self)
        elif key == "r":
            try:
                self.master.replay_request(self.flow)
            except exceptions.ReplayException as e:
                signals.add_log("Replay error: %s" % e, "warn")
            signals.flowlist_change.send(self)
        elif key == "S":
            def stop_server_playback(response):
                if response == "y":
                    self.master.options.server_replay = []
            a = self.master.addons.get("serverplayback")
            if a.count():
                signals.status_prompt_onekey.send(
                    prompt = "Stop current server replay?",
                    keys = (
                        ("yes", "y"),
                        ("no", "n"),
                    ),
                    callback = stop_server_playback,
                )
            else:
                signals.status_prompt_onekey.send(
                    prompt = "Server Replay",
                    keys = (
                        ("all flows", "a"),
                        ("this flow", "t"),
                    ),
                    callback = self.server_replay_prompt,
                )
        elif key == "U":
            for f in self.master.view:
                f.marked = False
            signals.flowlist_change.send(self)
        elif key == "V":
            if not self.flow.modified():
                signals.status_message.send(message="Flow not modified.")
                return
            self.flow.revert()
            signals.flowlist_change.send(self)
            signals.status_message.send(message="Reverted.")
        elif key == "w":
            signals.status_prompt_onekey.send(
                self,
                prompt = "Save",
                keys = (
                    ("listed flows", "l"),
                    ("this flow", "t"),
                ),
                callback = self.save_flows_prompt,
            )
        elif key == "X":
            if self.flow.killable:
                self.flow.kill(self.master)
        elif key == "enter":
            if self.flow.request:
                self.master.view_flow(self.flow)
        elif key == "|":
            signals.status_prompt_path.send(
                prompt = "Send flow to script",
                callback = self.master.run_script_once,
                args = (self.flow,)
            )
        elif key == "E":
            signals.status_prompt_onekey.send(
                self,
                prompt = "Export to file",
                keys = [(e[0], e[1]) for e in export.EXPORTERS],
                callback = common.export_to_clip_or_file,
                args = (None, self.flow, common.ask_save_path)
            )
        elif key == "C":
            signals.status_prompt_onekey.send(
                self,
                prompt = "Export to clipboard",
                keys = [(e[0], e[1]) for e in export.EXPORTERS],
                callback = common.export_to_clip_or_file,
                args = (None, self.flow, common.copy_to_clipboard_or_prompt)
            )
        elif key == "b":
            common.ask_save_body(None, self.flow)
        else:
            return key