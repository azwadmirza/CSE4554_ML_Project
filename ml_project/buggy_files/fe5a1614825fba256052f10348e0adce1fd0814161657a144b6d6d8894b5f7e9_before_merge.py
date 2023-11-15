    def create_lcd_line(self, last_measurement_success, i):
        try:
            if last_measurement_success:
                # Determine if the LCD output will have a value unit
                measurement = ''
                if self.lcd_line[i]['measurement'] == 'setpoint':
                    pid = db_retrieve_table_daemon(
                        PID, unique_id=self.lcd_line[i]['id'])
                    measurement = pid.measurement
                    self.lcd_line[i]['measurement_value'] = '{:.2f}'.format(
                        self.lcd_line[i]['measurement_value'])
                elif self.lcd_line[i]['measurement'] == 'duration_sec':
                    measurement = 'duration_sec'
                    self.lcd_line[i]['measurement_value'] = '{:.2f}'.format(
                        self.lcd_line[i]['measurement_value'])
                elif self.lcd_line[i]['measurement'] in MEASUREMENT_UNITS:
                    measurement = self.lcd_line[i]['measurement']

                # Produce the line that will be displayed on the LCD
                number_characters = self.lcd_x_characters
                if self.lcd_line[i]['measurement'] == 'time':
                    # Convert UTC timestamp to local timezone
                    utc_dt = datetime.datetime.strptime(
                        self.lcd_line[i]['time'].split(".")[0],
                        '%Y-%m-%dT%H:%M:%S')
                    utc_timestamp = calendar.timegm(utc_dt.timetuple())
                    self.lcd_string_line[i] = str(
                        datetime.datetime.fromtimestamp(utc_timestamp))
                elif measurement:
                    value_length = len(str(
                        self.lcd_line[i]['measurement_value']))
                    unit_length = len(MEASUREMENT_UNITS[measurement]['unit'])
                    name_length = number_characters - value_length - unit_length - 2
                    name_cropped = self.lcd_line[i]['name'].ljust(name_length)[:name_length]
                    self.lcd_string_line[i] = u'{name} {value} {unit}'.format(
                        name=name_cropped,
                        value=self.lcd_line[i]['measurement_value'],
                        unit=MEASUREMENT_UNITS[measurement]['unit'])
                else:
                    value_length = len(str(
                        self.lcd_line[i]['measurement_value']))
                    name_length = number_characters - value_length - 1
                    name_cropped = self.lcd_line[i]['name'][:name_length]
                    self.lcd_string_line[i] = u'{name} {value}'.format(
                        name=name_cropped,
                        value=self.lcd_line[i]['measurement_value'])
            else:
                self.lcd_string_line[i] = 'ERROR: NO DATA'
        except Exception as except_msg:
            self.logger.exception("Error: {err}".format(err=except_msg))