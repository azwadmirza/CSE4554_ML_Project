def create_value_transform(echo_nostr, echo_noarr):
    def value_transform(val, type_information=None):
        def transform_field_value(value, value_type, echo_nostr, echo_noarr):
            if echo_noarr and '[' in value_type:
                return '<array type: %s, length: %s>' % \
                    (value_type.rstrip('[]'), len(value))
            elif echo_nostr and value_type == 'string':
                return '<string length: %s>' % len(value)
            elif echo_nostr and value_type == 'string[]':
                return '<array type: string, length: %s>' % len(value)
            return value

        if not isinstance(val, genpy.Message):
            if type_information is None:
                return val
            return transform_field_value(val, type_information,
                                         echo_nostr, echo_noarr)

        class TransformedMessage(genpy.Message):
            # These should be copy because changing these variables
            # in transforming is problematic without its untransforming.
            __slots__ = val.__slots__[:]
            _slot_types = val._slot_types[:]

        val_trans = TransformedMessage()

        fields = val.__slots__
        field_types = val._slot_types
        for index, (f, t) in enumerate(zip(fields, field_types)):
            f_val = getattr(val, f)
            f_val_trans = transform_field_value(f_val, t,
                                                echo_nostr, echo_noarr)
            if f_val_trans != f_val:
                setattr(val_trans, f, f_val_trans)
                val_trans._slot_types[index] = 'string'
            else:
                try:
                    msg_class = genpy.message.get_message_class(t)
                    if msg_class is None:
                        # happens for list of ROS messages like std_msgs/String[]
                        raise ValueError
                    nested_transformed = value_transform(f_val)
                    setattr(val_trans, f, nested_transformed)
                except ValueError:
                    setattr(val_trans, f, f_val)
        return val_trans
    return value_transform