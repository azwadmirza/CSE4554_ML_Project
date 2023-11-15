    def load_config(self, config, return_error=False, opts=None):
        """Sends configuration commands to the remote device
        """
        if opts is None:
            opts = {}

        connection = self._get_connection()

        msgs = []
        try:
            responses = connection.edit_config(config)
            out = json.loads(responses)[1:-1]
            msg = out
        except ConnectionError as e:
            code = getattr(e, 'code', 1)
            message = getattr(e, 'err', e)
            err = to_text(message, errors='surrogate_then_replace')
            if opts.get('ignore_timeout') and code:
                msgs.append(code)
                return msgs
            elif code and 'no graceful-restart' in err:
                if 'ISSU/HA will be affected if Graceful Restart is disabled' in err:
                    msg = ['']
                    msgs.extend(msg)
                    return msgs
                else:
                    self._module.fail_json(msg=err)
            elif code:
                self._module.fail_json(msg=err)

        msgs.extend(msg)
        return msgs