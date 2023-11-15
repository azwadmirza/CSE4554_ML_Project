    def find_next(self, backwards):
        if not self.search_term:
            if self.state.last_search:
                self.search_term = self.state.last_search
            else:
                self.set_highlight(None)
                return
        # Start search at focus + 1
        if backwards:
            rng = range(len(self.body) - 1, -1, -1)
        else:
            rng = range(1, len(self.body) + 1)
        for i in rng:
            off = (self.focus_position + i) % len(self.body)
            w = self.body[off]
            txt = self.get_text(w)
            if txt and self.search_term in txt:
                self.set_highlight(off)
                self.set_focus(off, coming_from="above")
                self.body._modified()
                return
        else:
            self.set_highlight(None)
            signals.status_message.send(message="Search not found.", expire=1)