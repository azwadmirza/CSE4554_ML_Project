    def _set_call_return_value(self, call_dict, data, is_error=False):
        """
        A remote call has just been processed.

        This will reply if settings['blocking'] == True
        """
        settings = call_dict['settings']
        send_reply = 'send_reply' in settings and settings['send_reply']

        if not send_reply and not is_error:
            # Nothing to send back
            return
        content = {
            'is_error': is_error,
            'call_id': call_dict['call_id'],
            'call_name': call_dict['call_name']
        }

        self._send_message('remote_call_reply', content=content, data=data,
                           comm_id=self.calling_comm_id)