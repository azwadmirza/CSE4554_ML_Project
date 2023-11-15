    def evaluate(self, image_obj, context):
        attr = self.attribute.value()
        check = self.check.value()
        rval = self.check_value.value()

        if not attr or not check:
            return

        op = self.__ops__.get(check)
        if op is None or op.requires_rvalue and not rval:
            # Raise exception or fall thru
            return

        img_val = self.__valid_attributes__[attr][0](image_obj)
        # Make consistent types (specifically for int/float/str)
        if type(img_val) in [int, float, str]:
            if attr == 'size':
                rval = convert_bytes_size(rval)
            else:
                rval = type(img_val)(rval)

        if op.eval_function(img_val, rval):
            self._fire(msg="Attribute check for attribute: '{}' check: '{}' check_value: '{}' matched image value: '{}'".format(attr, check, (str(rval) if rval is not None else ''), img_val))