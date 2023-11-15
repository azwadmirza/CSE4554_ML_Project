    def _check_type_jsonarg(self, value):
        # Return a jsonified string.  Sometimes the controller turns a json
        # string into a dict/list so transform it back into json here
        if isinstance(value, (text_type, binary_type)):
            return value.strip()
        else:
            if isinstance(value, (list, tuple, dict)):
                return self.jsonify(value)
        raise TypeError('%s cannot be converted to a json string' % type(value))