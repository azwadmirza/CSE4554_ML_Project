    def keypress(self, size, key):
        key = common.shortcuts(key)
        if key == "A":
            for f in self.master.view:
                if f.intercepted:
                    f.resume(self.master)
            signals.flowlist_change.send(self)
        elif key == "z":
            self.master.view.clear()
        elif key == "e":
            self.master.toggle_eventlog()
        elif key == "g":
            self.master.view.focus.index = 0
        elif key == "G":
            self.master.view.focus.index = len(self.master.view) - 1
        elif key == "f":
            signals.status_prompt.send(
                prompt = "Filter View",
                text = self.master.options.filter,
                callback = self.master.options.setter("filter")
            )
        elif key == "L":
            signals.status_prompt_path.send(
                self,
                prompt = "Load flows",
                callback = self.master.load_flows_callback
            )
        elif key == "n":
            signals.status_prompt_onekey.send(
                prompt = "Method",
                keys = common.METHOD_OPTIONS,
                callback = self.get_method
            )
        elif key == "o":
            orders = [(i[1], i[0]) for i in view.orders]
            lookup = dict([(i[0], i[1]) for i in view.orders])

            def change_order(k):
                self.master.options.order = lookup[k]

            signals.status_prompt_onekey.send(
                prompt = "Order",
                keys = orders,
                callback = change_order
            )
        elif key == "F":
            o = self.master.options
            o.focus_follow = not o.focus_follow
        elif key == "v":
            val = not self.master.options.order_reversed
            self.master.options.order_reversed = val
        elif key == "W":
            if self.master.options.streamfile:
                self.master.options.streamfile = None
            else:
                signals.status_prompt_path.send(
                    self,
                    prompt="Stream flows to",
                    callback= lambda path: self.master.options.update(streamfile=path)
                )
        else:
            return urwid.ListBox.keypress(self, size, key)