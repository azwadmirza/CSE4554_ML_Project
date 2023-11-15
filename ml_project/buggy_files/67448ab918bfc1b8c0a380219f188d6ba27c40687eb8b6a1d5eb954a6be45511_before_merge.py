    def keypress(self, size, key):
        key = super(self.__class__, self).keypress(size, key)

        if key == " ":
            self.view_next_flow(self.flow)
            return

        key = common.shortcuts(key)
        if self.tab_offset == TAB_REQ:
            conn = self.flow.request
        elif self.tab_offset == TAB_RESP:
            conn = self.flow.response
        else:
            conn = None

        if key in ("up", "down", "page up", "page down"):
            # Why doesn't this just work??
            self._w.keypress(size, key)
        elif key == "a":
            self.flow.accept_intercept(self.master)
            signals.flow_change.send(self, flow = self.flow)
        elif key == "A":
            self.master.accept_all()
            signals.flow_change.send(self, flow = self.flow)
        elif key == "d":
            if self.state.flow_count() == 1:
                self.master.view_flowlist()
            elif self.state.view.index(self.flow) == len(self.state.view) - 1:
                self.view_prev_flow(self.flow)
            else:
                self.view_next_flow(self.flow)
            f = self.flow
            f.kill(self.master)
            self.state.delete_flow(f)
        elif key == "D":
            f = self.master.duplicate_flow(self.flow)
            signals.pop_view_state.send(self)
            self.master.view_flow(f)
            signals.status_message.send(message="Duplicated.")
        elif key == "p":
            self.view_prev_flow(self.flow)
        elif key == "r":
            r = self.master.replay_request(self.flow)
            if r:
                signals.status_message.send(message=r)
            signals.flow_change.send(self, flow = self.flow)
        elif key == "V":
            if not self.flow.modified():
                signals.status_message.send(message="Flow not modified.")
                return
            self.state.revert(self.flow)
            signals.flow_change.send(self, flow = self.flow)
            signals.status_message.send(message="Reverted.")
        elif key == "W":
            signals.status_prompt_path.send(
                prompt = "Save this flow",
                callback = self.master.save_one_flow,
                args = (self.flow,)
            )
        elif key == "|":
            signals.status_prompt_path.send(
                prompt = "Send flow to script",
                callback = self.master.run_script_once,
                args = (self.flow,)
            )

        if not conn and key in set(list("befgmxvzEC")):
            signals.status_message.send(
                message = "Tab to the request or response",
                expire = 1
            )
        elif conn:
            if key == "b":
                if self.tab_offset == TAB_REQ:
                    common.ask_save_body(
                        "q", self.flow
                    )
                else:
                    common.ask_save_body(
                        "s", self.flow
                    )
            elif key == "e":
                if self.tab_offset == TAB_REQ:
                    signals.status_prompt_onekey.send(
                        prompt = "Edit request",
                        keys = (
                            ("cookies", "c"),
                            ("query", "q"),
                            ("path", "p"),
                            ("url", "u"),
                            ("header", "h"),
                            ("form", "f"),
                            ("raw body", "r"),
                            ("method", "m"),
                        ),
                        callback = self.edit
                    )
                else:
                    signals.status_prompt_onekey.send(
                        prompt = "Edit response",
                        keys = (
                            ("cookies", "c"),
                            ("code", "o"),
                            ("message", "m"),
                            ("header", "h"),
                            ("raw body", "r"),
                        ),
                        callback = self.edit
                    )
                key = None
            elif key == "f":
                signals.status_message.send(message="Loading all body data...")
                self.state.add_flow_setting(
                    self.flow,
                    (self.tab_offset, "fullcontents"),
                    True
                )
                signals.flow_change.send(self, flow = self.flow)
                signals.status_message.send(message="")
            elif key == "m":
                p = list(contentviews.view_prompts)
                p.insert(0, ("Clear", "C"))
                signals.status_prompt_onekey.send(
                    self,
                    prompt = "Display mode",
                    keys = p,
                    callback = self.change_this_display_mode
                )
                key = None
            elif key == "E":
                if self.tab_offset == TAB_REQ:
                    scope = "q"
                else:
                    scope = "s"
                signals.status_prompt_onekey.send(
                    self,
                    prompt = "Export to file",
                    keys = [(e[0], e[1]) for e in export.EXPORTERS],
                    callback = common.export_to_clip_or_file,
                    args = (scope, self.flow, common.ask_save_path)
                )
            elif key == "C":
                if self.tab_offset == TAB_REQ:
                    scope = "q"
                else:
                    scope = "s"
                signals.status_prompt_onekey.send(
                    self,
                    prompt = "Export to clipboard",
                    keys = [(e[0], e[1]) for e in export.EXPORTERS],
                    callback = common.export_to_clip_or_file,
                    args = (scope, self.flow, common.copy_to_clipboard_or_prompt)
                )
            elif key == "x":
                signals.status_prompt_onekey.send(
                    prompt = "Delete body",
                    keys = (
                        ("completely", "c"),
                        ("mark as missing", "m"),
                    ),
                    callback = self.delete_body
                )
                key = None
            elif key == "v":
                if conn.raw_content:
                    t = conn.headers.get("content-type")
                    if "EDITOR" in os.environ or "PAGER" in os.environ:
                        self.master.spawn_external_viewer(conn.get_content(strict=False), t)
                    else:
                        signals.status_message.send(
                            message = "Error! Set $EDITOR or $PAGER."
                        )
            elif key == "z":
                self.flow.backup()
                e = conn.headers.get("content-encoding", "identity")
                if e != "identity":
                    if not conn.decode():
                        signals.status_message.send(
                            message = "Could not decode - invalid data?"
                        )
                else:
                    signals.status_prompt_onekey.send(
                        prompt = "Select encoding: ",
                        keys = (
                            ("gzip", "z"),
                            ("deflate", "d"),
                        ),
                        callback = self.encode_callback,
                        args = (conn,)
                    )
                signals.flow_change.send(self, flow = self.flow)
        return key