    def get_serial_number(self):
        """Return the serial number in the certificate."""
        return bytes_to_str(self._cert.get_serial_number())