    def process_completion(self, params):
        """Handle completion response."""
        args = self.completion_args
        if args is None:
            # This should not happen
            return
        self.completion_args = None
        position, automatic = args
        try:
            completions = params['params']
            completions = ([] if completions is None else
                           [completion for completion in completions
                            if completion['insertText']])

            replace_end = self.textCursor().position()
            under_cursor = self.get_current_word_and_position(completion=True)
            if under_cursor:
                word, replace_start = under_cursor
            else:
                word = ''
                replace_start = replace_end
            first_letter = ''
            if len(word) > 0:
                first_letter = word[0]

            def sort_key(completion):
                if 'textEdit' in completion:
                    first_insert_letter = completion['textEdit']['newText'][0]
                else:
                    first_insert_letter = completion['insertText'][0]
                case_mismatch = (
                    (first_letter.isupper() and first_insert_letter.islower())
                    or
                    (first_letter.islower() and first_insert_letter.isupper())
                )
                # False < True, so case matches go first
                return (case_mismatch, completion['sortText'])

            completion_list = sorted(completions, key=sort_key)

            # Allow for textEdit completions to be filtered by Spyder
            # if on-the-fly completions are disabled, only if the
            # textEdit range matches the word under the cursor.
            for completion in completion_list:
                if 'textEdit' in completion:
                    c_replace_start = completion['textEdit']['range']['start']
                    c_replace_end = completion['textEdit']['range']['end']
                    if (c_replace_start == replace_start
                            and c_replace_end == replace_end):
                        insert_text = completion['textEdit']['newText']
                        completion['filterText'] = insert_text
                        completion['insertText'] = insert_text
                        del completion['textEdit']

            if len(completion_list) > 0:
                self.completion_widget.show_list(
                        completion_list, position, automatic)

            self.kite_call_to_action.handle_processed_completions(completions)
        except RuntimeError:
            # This is triggered when a codeeditor instance has been
            # removed before the response can be processed.
            self.kite_call_to_action.hide_coverage_cta()
            return
        except Exception:
            self.log_lsp_handle_errors('Error when processing completions')