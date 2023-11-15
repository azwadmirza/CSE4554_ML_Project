def create_value_transform(echo_nostr, echo_noarr):
    def value_transform(val):

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
            if echo_noarr and '[' in t:
                setattr(val_trans, f, '<array type: %s, length: %s>' %
                                      (t.rstrip('[]'), len(f_val)))
                val_trans._slot_types[index] = 'string'
            elif echo_nostr and 'string' in t:
                setattr(val_trans, f, '<string length: %s>' % len(f_val))
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