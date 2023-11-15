def get_smart_data():
    """
    Get SMART attribute data
    :return: list of multi leveled dictionaries
             each dict has a key "DeviceName" with the identification of the device in smartctl
             also has keys of the SMART attribute id, with value of another dict of the attributes
             [
                {
                    "DeviceName": "/dev/sda blahblah",
                    "1":
                    {
                        "flags": "..",
                        "raw": "..",
                        etc,
                    }
                    ...
                }
             ]
    """
    stats = []
    # get all devices
    devlist = DeviceList()

    for dev in devlist.devices:
        stats.append({
            'DeviceName': '{} {}'.format(dev.name, dev.model),
        })
        for attribute in dev.attributes:
            if attribute is None:
                pass
            else:
                attribdict = convert_attribute_to_dict(attribute)

                # we will use the attribute number as the key
                num = attribdict.pop('num', None)
                try:
                    assert num is not None
                except Exception as e:
                    # we should never get here, but if we do, continue to next iteration and skip this attribute
                    continue

                stats[-1][num] = attribdict
    return stats