    def keypress(self, xxx_todo_changeme, key):
        (maxcol,) = xxx_todo_changeme
        key = common.shortcuts(key)
        if key == "a":
            self.flow.accept_intercept(self.master)
            signals.flowlist_change.send(self)
        elif key == "d":
            if not self.flow.reply.acked:
                self.flow.kill(self.master)
            self.state.delete_flow(self.flow)
            signals.flowlist_change.send(self)
        elif key == "D":
            f = self.master.duplicate_flow(self.flow)
            self.master.state.set_focus_flow(f)
            signals.flowlist_change.send(self)
        elif key == "m":
            if self.state.flow_marked(self.flow):
                self.state.set_flow_marked(self.flow, False)
            else:
                self.state.set_flow_marked(self.flow, True)
            signals.flowlist_change.send(self)
        elif key == "M":
            if self.state.mark_filter:
                self.state.disable_marked_filter()
            else:
                self.state.enable_marked_filter()
            signals.flowlist_change.send(self)
        elif key == "r":
            r = self.master.replay_request(self.flow)
            if r:
                signals.status_message.send(message=r)
            signals.flowlist_change.send(self)
        elif key == "S":
            if not self.master.server_playback:
                signals.status_prompt_onekey.send(
                    prompt = "Server Replay",
                    keys = (
                        ("all flows", "a"),
                        ("this flow", "t"),
                        ("file", "f"),
                    ),
                    callback = self.server_replay_prompt,
                )
            else:
                signals.status_prompt_onekey.send(
                    prompt = "Stop current server replay?",
                    keys = (
                        ("yes", "y"),
                        ("no", "n"),
                    ),
                    callback = self.stop_server_playback_prompt,
                )
        elif key == "U":
            for f in self.state.flows:
                self.state.set_flow_marked(f, False)
            signals.flowlist_change.send(self)
        elif key == "V":
            if not self.flow.modified():
                signals.status_message.send(message="Flow not modified.")
                return
            self.state.revert(self.flow)
            signals.flowlist_change.send(self)
            signals.status_message.send(message="Reverted.")
        elif key == "w":
            signals.status_prompt_onekey.send(
                self,
                prompt = "Save",
                keys = (
                    ("all flows", "a"),
                    ("this flow", "t"),
                    ("marked flows", "m"),
                ),
                callback = self.save_flows_prompt,
            )
        elif key == "X":
            if not self.flow.reply.acked:
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