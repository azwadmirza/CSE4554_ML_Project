    def process_signature(self, response):
        params = None
        calls = response['calls']
        if len(calls) > 0:
            call = calls[0]
            callee = call['callee']
            documentation = callee['synopsis']
            call_label = callee['repr']
            signatures = call['signatures']
            arg_idx = call['arg_index']

            signature = signatures[0]
            parameters = []
            names = []
            logger.debug(signature)
            for arg in signature['args']:
                parameters.append({
                    'label': arg['name'],
                    'documentation': ''
                })
                names.append(arg['name'])

            func_args = ', '.join(names)
            call_label = '{0}({1})'.format(call_label, func_args)

            base_signature = {
                'label': call_label,
                'documentation': documentation,
                'parameters': parameters
            }
            # doc_signatures.append(base_signature)
            params = {
                'signatures': base_signature,
                'activeSignature': 0,
                'activeParameter': arg_idx
            }
        return {'params': params}