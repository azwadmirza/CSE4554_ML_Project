    def _write(self, data):
        assert len(data) <= _REPORT_LENGTH
        packet = bytearray(1 + _REPORT_LENGTH)
        packet[1 : 1 + len(data)] = data  # device doesn't use numbered reports
        self.device.write(packet)