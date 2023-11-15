    def get_data_reader(self, enc_dtype):
        # _data_type dictionary.
        # The first element of the InfoArray in the TagType
        # will always be one of _data_type keys.
        # the tuple reads: ('read bytes function', 'number of bytes', 'type')

        dtype_dict = {
            2: (iou.read_short, 2, 'h'),
            3: (iou.read_long, 4, 'l'),
            4: (iou.read_ushort, 2, 'H'),  # dm3 uses ushorts for unicode chars
            5: (iou.read_ulong, 4, 'L'),
            6: (iou.read_float, 4, 'f'),
            7: (iou.read_double, 8, 'd'),
            8: (iou.read_boolean, 1, 'B'),
            # dm3 uses chars for 1-Byte signed integers
            9: (iou.read_char, 1, 'b'),
            10: (iou.read_byte, 1, 'b'),   # 0x0a
            11: (iou.read_long_long, 8, 'q'),  # long long, new in DM4
            # unsigned long long, new in DM4
            12: (iou.read_ulong_long, 8, 'Q'),
            15: (self.read_struct, None, 'struct',),  # 0x0f
            18: (self.read_string, None, 'c'),  # 0x12
            20: (self.read_array, None, 'array'),  # 0x14
        }
        return dtype_dict[enc_dtype]