    def jsonify(self, data):
        for encoding in ("utf-8", "latin-1"):
            try:
                return json.dumps(data, encoding=encoding, cls=_SetEncoder)
            # Old systems using old simplejson module does not support encoding keyword.
            except TypeError:
                try:
                    new_data = json_dict_bytes_to_unicode(data, encoding=encoding)
                except UnicodeDecodeError:
                    continue
                return json.dumps(new_data, cls=_SetEncoder)
            except UnicodeDecodeError:
                continue
        self.fail_json(msg='Invalid unicode encoding encountered')