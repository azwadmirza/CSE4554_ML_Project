    def get_completions(self, document, complete_event):
        """Returns a generator for list of completions."""

        #  Only generate completions when the user hits tab.
        if complete_event.completion_requested:
            line = document.current_line.lstrip()
            endidx = document.cursor_position_col
            begidx = line[:endidx].rfind(' ') + 1 if line[:endidx].rfind(' ') >= 0 else 0
            prefix = line[begidx:endidx]
            completions, l = self.completer.complete(prefix,
                                                     line,
                                                     begidx,
                                                     endidx,
                                                     self.ctx)
            if len(completions) <= 1:
                pass
            elif len(os.path.commonprefix(completions)) <= len(prefix):
                self.reserve_space()
            for comp in completions:
                yield Completion(comp, -l)