    def _notifications_handler(self, n):
        assert self.receiver
        # if _log.isEnabledFor(_DEBUG):
        #     _log.debug("%s: handling %s", self.receiver, n)
        if n.devnumber == 0xFF:
            # a receiver notification
            _notifications.process(self.receiver, n)
            return

        # a device notification
        if not (0 < n.devnumber <= self.receiver.max_devices):
            if _log.isEnabledFor(_WARNING):
                _log.warning(_('Unexpected device number (%s) in notification %s.' % (n.devnumber, n)))
            return
        already_known = n.devnumber in self.receiver

        # FIXME: hacky fix for kernel/hardware race condition
        # If the device was just turned on or woken up from sleep, it may not
        # be ready to receive commands. The "payload" bit of the wireless
        # status notification seems to tell us this. If this is the case, we
        # must wait a short amount of time to avoid causing a broken pipe
        # error.
        device_ready = not bool(ord(n.data[0:1]) & 0x80) or n.sub_id != 0x41
        if not device_ready:
            time.sleep(0.01)

        if n.sub_id == 0x40 and not already_known:
            return  # disconnecting something that is not known - nothing to do

        if n.sub_id == 0x41:
            if not already_known:
                dev = self.receiver.register_new_device(n.devnumber, n)
            elif self.receiver.status.lock_open and self.receiver.re_pairs and not ord(n.data[0:1]) & 0x40:
                dev = self.receiver[n.devnumber]
                del self.receiver[n.devnumber]  # get rid of information on device re-paired away
                self._status_changed(dev)  # signal that this device has changed
                dev = self.receiver.register_new_device(n.devnumber, n)
                self.receiver.status.new_device = self.receiver[n.devnumber]
            else:
                dev = self.receiver[n.devnumber]
        else:
            dev = self.receiver[n.devnumber]

        if not dev:
            _log.warn('%s: received %s for invalid device %d: %r', self.receiver, n, n.devnumber, dev)
            return

        # Apply settings every time the device connects
        if n.sub_id == 0x41:
            if _log.isEnabledFor(_INFO):
                _log.info('%s triggered new device %s (%s)', n, dev, dev.kind)
            # If there are saved configs, bring the device's settings up-to-date.
            # They will be applied when the device is marked as online.
            configuration.attach_to(dev)
            _status.attach_to(dev, self._status_changed)
            # the receiver changed status as well
            self._status_changed(self.receiver)

        assert dev
        assert dev.status is not None
        _notifications.process(dev, n)
        if self.receiver.status.lock_open and not already_known:
            # this should be the first notification after a device was paired
            assert n.sub_id == 0x41 and n.address == 0x04
            if _log.isEnabledFor(_INFO):
                _log.info('%s: pairing detected new device', self.receiver)
            self.receiver.status.new_device = dev
        elif dev.online is None:
            dev.ping()