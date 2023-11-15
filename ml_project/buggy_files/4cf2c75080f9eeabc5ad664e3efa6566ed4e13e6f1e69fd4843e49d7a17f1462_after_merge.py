    def _handle_stream(self, msg):
        """
        Reimplemented to handle input replies in hidden mode
        """
        if not self._hidden:
            self.flush_clearoutput()
            self.append_stream(msg['content']['text'])
            # This signal is a clear indication that all stdout
            # has been handled at this point. Then Spyder can
            # proceed to request other inputs
            self.sig_prompt_ready.emit()
        else:
            # This allows Spyder to receive, transform and save the
            # contents of a silent execution
            content = msg.get('content', '')
            if content:
                name = content.get('name', '')
                if name == 'stdout':
                    text = content['text']
                    text = to_text_string(text.replace('\n', ''))
                    try:
                        reply = ast.literal_eval(text)
                    except:
                        reply = None
                    if not isinstance(reply, dict):
                        self._input_reply = None
                    else:
                        self._input_reply = reply
                    self.sig_input_reply.emit()
                else:
                    self._input_reply = None
                    self.sig_input_reply.emit()
            else:
                self._input_reply = None
                self.sig_input_reply.emit()