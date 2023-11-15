        def _parse_cap(tag):
            elm = data.find(tag)
            return elm.get('supportedparams').split(',') if elm and elm.get('available') == 'yes' else []