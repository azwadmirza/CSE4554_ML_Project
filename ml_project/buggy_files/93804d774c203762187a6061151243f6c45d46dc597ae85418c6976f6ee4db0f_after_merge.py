def update_recording_bytes_to_unicode(rec_dir):
    logger.info("Updating recording from bytes to unicode.")

    # update to python 3
    meta_info_path = os.path.join(rec_dir, "info.csv")

    def convert(data):
        if isinstance(data, bytes):
            return data.decode()
        elif isinstance(data, str) or isinstance(data, np.ndarray):
            return data
        elif isinstance(data, collections.Mapping):
            return dict(map(convert, data.items()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(convert, data))
        else:
            return data

    for file in os.listdir(rec_dir):
        rec_file = os.path.join(rec_dir, file)
        try:
            rec_object = load_object(rec_file)
            converted_object = convert(rec_object)
            if converted_object != rec_object:
                logger.info('Converted `{}` from bytes to unicode'.format(file))
                save_object(rec_object, rec_file)
        except (ValueError, IsADirectoryError):
            continue
        # except TypeError:
        #     logger.error('TypeError when parsing `{}`'.format(file))
        #     continue

    with open(meta_info_path, 'r', encoding='utf-8') as csvfile:
        meta_info = csv_utils.read_key_value_file(csvfile)
        meta_info['Capture Software Version'] = 'v0.8.8'

    with open(meta_info_path, 'w', newline='') as csvfile:
        csv_utils.write_key_value_file(csvfile, meta_info)