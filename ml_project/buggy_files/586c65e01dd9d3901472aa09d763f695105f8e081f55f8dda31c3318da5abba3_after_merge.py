    def get_serial(self):
        """
        Get serial number for device

        :return: String of the serial number
        :rtype: str
        """
        # TODO raise exception if serial cant be got and handle during device add
        if self._serial is None:
            serial_path = os.path.join(self._device_path, 'device_serial')
            count = 0
            serial = ''
            while len(serial) == 0:
                if count >= 5:
                    break

                try:
                    with open(serial_path, 'r') as f:
                        serial = f.read().strip()
                except (PermissionError, OSError) as err:
                    self.logger.warning('getting serial: {0}'.format(err))
                    serial = ''
                except UnicodeDecodeError as err:
                    self.logger.warning('malformed serial: {0}'.format(err))
                    serial = ''

                count += 1
                time.sleep(0.1)

                if len(serial) == 0:
                    self.logger.debug('getting serial: {0} count:{1}'.format(serial, count))

            if serial == '' or serial == 'Default string' or serial == 'empty (NULL)' or serial == 'As printed in the D cover':
                serial = 'UNKWN{0:012}'.format(random.randint(0, 4096))

            self._serial = serial.replace(' ', '_')

        return self._serial