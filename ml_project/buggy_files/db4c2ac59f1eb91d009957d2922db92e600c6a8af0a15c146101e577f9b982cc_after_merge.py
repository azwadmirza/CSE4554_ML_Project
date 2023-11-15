            def decode(self_, data):
                if isinstance(data, text_type):  # py3: `data` already decoded.
                    return data
                return data.decode(self_.encoding, 'sphinx')  # py2: decoding