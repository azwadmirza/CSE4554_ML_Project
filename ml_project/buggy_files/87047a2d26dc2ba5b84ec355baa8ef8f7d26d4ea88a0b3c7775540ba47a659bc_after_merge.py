    def devices_detailed(increment=''):
        if increment is None:
            raise FileNotFoundError(
                "guiscrcpy couldn't find adb. "
                "Please specify path to adb in configuration filename"
            )
        proc = Popen(_(increment + " devices -l"), stdout=PIPE)
        output = [[y.strip() for y in x.split()]
                  for x in decode_process(proc)[1:]][:-1]
        devices_found = []
        for device in output:
            # https://github.com/srevinsaju/guiscrcpy/issues/117
            if 'udev' in device and 'permission' in device:
                # This is an error with some linux and Windows OSes
                # This happens because the udev is not configured
                # and linux adb does not have access to reading the device
                # the status hence should be 'no_permission'
                status = 'no_permission'
            else:
                status = device[1]
            description = {
                'identifier': device[0],
                'status': status,
                'product': get(device, 2, ':').split(':')[-1],
                'model': get(device, 3, ':').split(':')[-1],
                'device': get(device, 4, ':').split(':')[-1],
                'transport_id': get(device, 5, ':').split(':')[-1]
            }
            devices_found.append(description)
        logging.debug("ADB: {}".format(devices_found))
        return devices_found