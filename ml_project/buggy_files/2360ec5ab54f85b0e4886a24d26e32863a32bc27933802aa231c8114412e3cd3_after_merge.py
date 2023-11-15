    def __init__(self, ready, lcd_id):
        threading.Thread.__init__(self)

        self.logger = logging.getLogger("mycodo.lcd_{id}".format(id=lcd_id))

        self.running = False
        self.thread_startup_timer = timeit.default_timer()
        self.thread_shutdown_timer = 0
        self.ready = ready
        self.flash_lcd_on = False
        self.lcd_is_on = False
        self.lcd_id = lcd_id

        try:
            lcd = db_retrieve_table_daemon(LCD, device_id=self.lcd_id)

            self.lcd_name = lcd.name
            self.lcd_location = lcd.location
            self.lcd_period = lcd.period
            self.lcd_x_characters = lcd.x_characters
            self.lcd_y_lines = lcd.y_lines
            self.timer = time.time() + self.lcd_period
            self.backlight_timer = time.time()

            if lcd.multiplexer_address:
                self.multiplexer_address_string = lcd.multiplexer_address
                self.multiplexer_address = int(str(lcd.multiplexer_address),
                                               16)
                self.multiplexer_channel = lcd.multiplexer_channel
                self.multiplexer = TCA9548A(self.multiplexer_address)
            else:
                self.multiplexer = None

            self.lcd_line = {}
            for i in range(1, self.lcd_y_lines + 1):
                self.lcd_line[i] = {}

            self.list_pids = ['setpoint', 'pid_time']
            self.list_relays = ['duration_sec', 'relay_time', 'relay_state']

            self.list_sensors = MEASUREMENT_UNITS
            self.list_sensors.update(
                {'sensor_time': {'unit': None, 'name': 'Time'}})

            # Add custom measurement and units to list (From linux command sensor)
            sensor = db_retrieve_table_daemon(Sensor)
            self.list_sensors = add_custom_measurements(
                sensor, self.list_sensors, MEASUREMENT_UNITS)

            if self.lcd_y_lines in [2, 4]:
                self.setup_lcd_line(
                    1, lcd.line_1_sensor_id, lcd.line_1_measurement)
                self.setup_lcd_line(
                    2, lcd.line_2_sensor_id, lcd.line_2_measurement)

            if self.lcd_y_lines == 4:
                self.setup_lcd_line(
                    3, lcd.line_3_sensor_id, lcd.line_3_measurement)
                self.setup_lcd_line(
                    4, lcd.line_4_sensor_id, lcd.line_4_measurement)

            self.lcd_string_line = {}
            for i in range(1, self.lcd_y_lines + 1):
                self.lcd_string_line[i] = ''

            self.LCD_WIDTH = self.lcd_x_characters  # Max characters per line

            self.LCD_LINE = {
                1: 0x80,
                2: 0xC0,
                3: 0x94,
                4: 0xD4
            }

            self.LCD_CHR = 1  # Mode - Sending data
            self.LCD_CMD = 0  # Mode - SenLCDding command

            self.LCD_BACKLIGHT = 0x08  # On
            self.LCD_BACKLIGHT_OFF = 0x00  # Off

            self.ENABLE = 0b00000100  # Enable bit

            # Timing constants
            self.E_PULSE = 0.0005
            self.E_DELAY = 0.0005

            # Setup I2C bus
            try:
                if GPIO.RPI_REVISION == 2 or GPIO.RPI_REVISION == 3:
                    i2c_bus_number = 1
                else:
                    i2c_bus_number = 0
                self.bus = smbus.SMBus(i2c_bus_number)
            except Exception as except_msg:
                self.logger.exception(
                    "Could not initialize I2C bus: {err}".format(
                        err=except_msg))

            self.I2C_ADDR = int(self.lcd_location, 16)
            self.lcd_init()
            self.lcd_string_write('Mycodo {}'.format(MYCODO_VERSION),
                                  self.LCD_LINE[1])
            self.lcd_string_write(u'Start {}'.format(
                self.lcd_name), self.LCD_LINE[2])
        except Exception as except_msg:
            self.logger.exception("Error: {err}".format(err=except_msg))