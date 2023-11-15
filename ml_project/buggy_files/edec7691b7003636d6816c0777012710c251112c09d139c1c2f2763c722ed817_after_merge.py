        def _parse_cap(tag):
            elm = data.find(tag)
            is_supported = elm and all([elm.get('supportedparams'), elm.get('available') == 'yes'])
            return elm['supportedparams'].split(',') if is_supported else []