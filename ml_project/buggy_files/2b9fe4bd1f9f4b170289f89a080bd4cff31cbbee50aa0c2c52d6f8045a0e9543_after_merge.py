def write_dataset(fp, dataset, parent_encoding=default_encoding):
    """Write a Dataset dictionary to the file. Return the total length written.

    Attempt to correct ambiguous VR elements when explicit little/big
      encoding Elements that can't be corrected will be returned unchanged.
    """
    _harmonize_properties(dataset, fp)

    if not fp.is_implicit_VR and not dataset.is_original_encoding:
        dataset = correct_ambiguous_vr(dataset, fp.is_little_endian)

    dataset_encoding = dataset.get('SpecificCharacterSet', parent_encoding)

    fpStart = fp.tell()
    # data_elements must be written in tag order
    tags = sorted(dataset.keys())

    for tag in tags:
        # do not write retired Group Length (see PS3.5, 7.2)
        if tag.element == 0 and tag.group > 6:
            continue
        with tag_in_exception(tag):
            write_data_element(fp, dataset.get_item(tag), dataset_encoding)

    return fp.tell() - fpStart