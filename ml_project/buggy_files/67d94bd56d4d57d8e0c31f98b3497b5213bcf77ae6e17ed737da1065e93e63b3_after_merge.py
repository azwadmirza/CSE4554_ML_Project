    def process_signature(self, response):
        params = None
        if response is not None:
            calls = response['calls']
            if len(calls) > 0:
                call = calls[0]
                callee = call['callee']
                documentation = callee['synopsis']
                call_label = callee['repr']
                signatures = call['signatures']
                arg_idx = call['arg_index']

                parameters = []
                names = []

                logger.debug(signatures)
                if len(signatures) > 0:
                    signature = signatures[0]
                    logger.debug(signature)
                    if signature['args'] is not None:
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
                    'activeParameter': arg_idx,
                    'provider': KITE_COMPLETION
                }
        return {'params': params}