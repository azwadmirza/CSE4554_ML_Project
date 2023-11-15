    def _create_raw_wrapper_payload(self, cmd, environment=None):
        environment = {} if environment is None else environment

        payload = {
            'module_entry': to_text(base64.b64encode(to_bytes(cmd))),
            'powershell_modules': {},
            'actions': ['exec'],
            'exec': to_text(base64.b64encode(to_bytes(leaf_exec))),
            'environment': environment,
            'min_ps_version': None,
            'min_os_version': None
        }

        return json.dumps(payload)