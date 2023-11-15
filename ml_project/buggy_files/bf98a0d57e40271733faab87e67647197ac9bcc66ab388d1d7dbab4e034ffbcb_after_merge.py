        def notifications_hook(self, n):
            nonlocal known_devices
            assert n
            if n.devnumber == 0xFF:
                _notifications.process(receiver, n)
            elif n.sub_id == 0x41 and len(n.data) == _base._SHORT_MESSAGE_SIZE - 4:
                kd, known_devices = known_devices, None  # only process one connection notification
                if kd is not None:
                    if n.devnumber not in kd:
                        receiver.status.new_device = receiver.register_new_device(n.devnumber, n)
                    elif receiver.re_pairs:
                        del receiver[n.devnumber]  # get rid of information on device re-paired away
                        receiver.status.new_device = receiver.register_new_device(n.devnumber, n)