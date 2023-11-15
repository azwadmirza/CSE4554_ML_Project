    def AdvertisementWatcher_Received(sender, e):
        if sender == watcher:
            logger.debug("Received {0}.".format(_format_event_args(e)))
            if e.AdvertisementType == BluetoothLEAdvertisementType.ScanResponse:
                if e.BluetoothAddress not in scan_responses:
                    scan_responses[e.BluetoothAddress] = e
            else:
                if e.BluetoothAddress not in devices:
                    devices[e.BluetoothAddress] = e