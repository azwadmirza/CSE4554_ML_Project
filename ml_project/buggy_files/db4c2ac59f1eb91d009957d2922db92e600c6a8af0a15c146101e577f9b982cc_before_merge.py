            def decode(self_, data):
                if isinstance(data, text_type):
                    return data
                return data.decode(self_.encoding, 'sphinx')