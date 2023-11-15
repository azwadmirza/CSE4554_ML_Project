    def scan_devices_update_list_view(self):
        """
        Scan for new devices; and update the list view
        :return:
        """
        # self.devices_view.clear()
        paired_devices = []
        for index in range(self.devices_view.count()):
            paired_devices.append(self.devices_view.item(index))

        devices = adb.devices_detailed(adb.path)
        log(devices)
        for i in devices:

            if i['identifier'] not in config['device'].keys():
                device_paired_and_exists = False
                config['device'][i['identifier']] = {
                    'rotation': 0
                }
            else:
                device_paired_and_exists = True

            if config['device'].get('rotation', 0) in (-1, 0, 2):
                icon = ':/icons/icons/portrait_mobile_white.svg'
            else:
                icon = ':/icons/icons/landscape_mobile_white.svg'
            if i['status'] == 'offline':
                icon = ':/icons/icons/portrait_mobile_error.svg'
            elif i['status'] == 'unauthorized':
                icon = ':/icons/icons/portrait_mobile_warning.svg'

            # Check if device is unauthorized

            if i['status'] == "unauthorized":
                log("unauthorized device detected: Click Allow on your device")
                # The device is connected; and might/might't paired in the past
                # And is connected to the same IP address
                # It is possibly a bug with the connection;
                # Temporarily create a new QListItem to display the
                # device with the error
                paired = False
                device_paired_and_exists = False

                # Remove other devices with the same id and offline and
                # unauthorized
                self.remove_device_device_view(
                    i['identifier'],
                    statuses=['offline', 'unauthorized']
                )
                # Unauthorized device cannot be considered as a paired device
                devices_view_list_item = QListWidgetItem()
            else:
                # check if device is paired
                # if yes, just update the list item
                if not device_paired_and_exists:
                    paired = False
                    devices_view_list_item = QListWidgetItem()
                else:
                    for paired_device in paired_devices:
                        if paired_device.text().split()[0] == i['model']:
                            paired = True
                            devices_view_list_item = paired_device
                            # as we have found a paired device
                            # we know by assumption; there cannot be two
                            # devices with the same local IP address;
                            # lets scan the devices_view once more in a loop
                            # to check for any device with the same
                            # identifier and remove them; based on this same
                            # assumption
                            self.remove_device_device_view(
                                i['identifier'],
                                statuses=['offline', 'unauthorized']
                            )
                            break
                        elif paired_device.text().split()[1] ==\
                                i['identifier']:

                            devices_view_list_item = QListWidgetItem()
                            paired = False
                            break
                    else:
                        paired = False
                        devices_view_list_item = QListWidgetItem()

            devices_view_list_item.setIcon(QIcon(icon))

            devices_view_list_item.setText(
                "{device}\n{mode}\n{status}".format(
                    device=i['model'],
                    mode=i['identifier'],
                    status=i['status']
                )
            )
            devices_view_list_item.setToolTip(
                "Device: {d}\n"
                "Model: {m}\n"
                "Alias: {a}\n"
                "Status: {s}\n"
                "Transport ID: {t}\n"
                "Paired: {p}".format(
                    d=i['identifier'],
                    m=i['model'],
                    a=i['product'],
                    s=i['status'],
                    t=i['transport_id'],
                    p=paired
                )
            )

            devices_view_list_item.setFont(QFont('Noto Sans', pointSize=8))
            log(device_paired_and_exists)
            if device_paired_and_exists:
                continue
            # If and only if the device doesn't exist; add it
            self.devices_view.addItem(devices_view_list_item)
        return devices