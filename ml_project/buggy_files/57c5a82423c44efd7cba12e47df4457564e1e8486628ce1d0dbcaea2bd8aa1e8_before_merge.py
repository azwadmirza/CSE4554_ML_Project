    def _handle_inspect_reply(self, rep):
        """
        Reimplement call tips to only show signatures, using the same
        style from our Editor and External Console too
        """
        cursor = self._get_cursor()
        info = self._request_info.get('call_tip')
        if (info and info.id == rep['parent_header']['msg_id'] and
                info.pos == cursor.position()):
            content = rep['content']
            if content.get('status') == 'ok' and content.get('found', False):
                signature = self.get_signature(content)
                documentation = self.get_documentation(content)
                if signature:
                    self._control.show_calltip(
                        signature,
                        documentation=documentation,
                        language=self.language_name,
                        max_lines=5
                    )