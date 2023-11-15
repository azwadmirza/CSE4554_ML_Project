def process_notification(device, status, notification, feature):
    global keys_down, key_down
    key_down = None
    # need to keep track of keys that are down to find a new key down
    if feature == _F.REPROG_CONTROLS_V4 and notification.address == 0x00:
        new_keys_down = _unpack('!4H', notification.data[:8])
        for key in new_keys_down:
            if key and key not in keys_down:
                key_down = key
        keys_down = new_keys_down
    rules.evaluate(feature, notification, device, status, True)