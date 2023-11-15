    def handle_response(self, response: 'Optional[Dict]'):
        global resolvable_completion_items

        if self.state == CompletionState.REQUESTING:
            items = []  # type: List[Dict]
            if isinstance(response, dict):
                items = response["items"]
            elif isinstance(response, list):
                items = response
            items = sorted(items, key=lambda item: item.get("sortText") or item["label"])
            self.completions = list(self.format_completion(item) for item in items)

            if self.has_resolve_provider:
                resolvable_completion_items = items

            # if insert_best_completion was just ran, undo it before presenting new completions.
            prev_char = self.view.substr(self.view.sel()[0].begin() - 1)
            if prev_char.isspace():
                if last_text_command == "insert_best_completion":
                    self.view.run_command("undo")

            self.state = CompletionState.APPLYING
            self.view.run_command("hide_auto_complete")
            self.run_auto_complete()
        elif self.state == CompletionState.CANCELLING:
            if self.next_request:
                prefix, locations = self.next_request
                self.do_request(prefix, locations)
                self.state = CompletionState.IDLE
        else:
            debug('Got unexpected response while in state {}'.format(self.state))