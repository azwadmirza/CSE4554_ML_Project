                        def add(our_key, wp_key, is_int=False, ignore_zero=False):
                            if wp_key in image_meta:
                                value = image_meta[wp_key]
                                if is_int:
                                    value = int(value)
                                    if ignore_zero and value == 0:
                                        return
                                else:
                                    value = value.decode('utf-8')  # assume UTF-8
                                    if value == '':  # skip empty values
                                        return
                                dst_meta[our_key] = value