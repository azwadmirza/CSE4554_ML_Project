def sensor_add(form_add_sensor):
    action = u'{action} {controller}'.format(
        action=gettext(u"Add"),
        controller=gettext(u"Sensor"))
    error = []

    if form_add_sensor.validate():
        for _ in range(0, form_add_sensor.numberSensors.data):
            new_sensor = Sensor()
            new_sensor.device = form_add_sensor.sensor.data
            new_sensor.name = '{name} Sensor'.format(name=form_add_sensor.sensor.data)
            if GPIO.RPI_INFO['P1_REVISION'] in [2, 3]:
                new_sensor.i2c_bus = 1
                new_sensor.multiplexer_bus = 1
            else:
                new_sensor.i2c_bus = 0
                new_sensor.multiplexer_bus = 0

            # Linux command as sensor
            if form_add_sensor.sensor.data == 'LinuxCommand':
                new_sensor.cmd_command = 'shuf -i 50-70 -n 1'
                new_sensor.cmd_measurement = 'Condition'
                new_sensor.cmd_measurement_units = 'unit'

            # Process monitors
            elif form_add_sensor.sensor.data == 'MYCODO_RAM':
                new_sensor.measurements = 'disk_space'
                new_sensor.location = 'Mycodo_daemon'
            elif form_add_sensor.sensor.data == 'RPi':
                new_sensor.measurements = 'temperature'
                new_sensor.location = 'RPi'
            elif form_add_sensor.sensor.data == 'RPiCPULoad':
                new_sensor.measurements = 'cpu_load_1m,' \
                                          'cpu_load_5m,' \
                                          'cpu_load_15m'
                new_sensor.location = 'RPi'
            elif form_add_sensor.sensor.data == 'RPiFreeSpace':
                new_sensor.measurements = 'disk_space'
                new_sensor.location = '/'
            elif form_add_sensor.sensor.data == 'EDGE':
                new_sensor.measurements = 'edge'

            # Environmental Sensors
            # Temperature
            elif form_add_sensor.sensor.data in ['ATLAS_PT1000_I2C',
                                                 'ATLAS_PT1000_UART',
                                                 'DS18B20',
                                                 'TMP006']:
                new_sensor.measurements = 'temperature'
                if form_add_sensor.sensor.data == 'ATLAS_PT1000_I2C':
                    new_sensor.interface = 'I2C'
                    new_sensor.location = '0x66'
                elif form_add_sensor.sensor.data == 'ATLAS_PT1000_UART':
                    new_sensor.location = 'Tx/Rx'
                    new_sensor.interface = 'UART'
                    new_sensor.baud_rate = 9600
                    if GPIO.RPI_INFO['P1_REVISION'] == 3:
                        new_sensor.device_loc = "/dev/ttyS0"
                    else:
                        new_sensor.device_loc = "/dev/ttyAMA0"
                elif form_add_sensor.sensor.data == 'TMP006':
                    new_sensor.measurements = 'temperature_object,' \
                                              'temperature_die'
                    new_sensor.location = '0x40'

            # Temperature/Humidity
            elif form_add_sensor.sensor.data in ['AM2315', 'DHT11',
                                                 'DHT22', 'HTU21D',
                                                 'SHT1x_7x', 'SHT2x']:
                new_sensor.measurements = 'temperature,humidity,dewpoint'
                if form_add_sensor.sensor.data == 'AM2315':
                    new_sensor.location = '0x5c'
                elif form_add_sensor.sensor.data == 'HTU21D':
                    new_sensor.location = '0x40'
                elif form_add_sensor.sensor.data == 'SHT2x':
                    new_sensor.location = '0x40'

            # Chirp moisture sensor
            elif form_add_sensor.sensor.data == 'CHIRP':
                new_sensor.measurements = 'lux,moisture,temperature'
                new_sensor.location = '0x20'

            # CO2
            elif form_add_sensor.sensor.data == 'MH_Z16_I2C':
                new_sensor.measurements = 'co2'
                new_sensor.location = '0x63'
                new_sensor.interface = 'I2C'
            elif form_add_sensor.sensor.data in ['K30_UART',
                                                 'MH_Z16_UART',
                                                 'MH_Z19_UART']:
                new_sensor.measurements = 'co2'
                new_sensor.location = 'Tx/Rx'
                new_sensor.interface = 'UART'
                new_sensor.baud_rate = 9600
                if GPIO.RPI_INFO['P1_REVISION'] == 3:
                    new_sensor.device_loc = "/dev/ttyS0"
                else:
                    new_sensor.device_loc = "/dev/ttyAMA0"

            # pH
            elif form_add_sensor.sensor.data == 'ATLAS_PH_I2C':
                new_sensor.measurements = 'ph'
                new_sensor.location = '0x63'
                new_sensor.interface = 'I2C'
            elif form_add_sensor.sensor.data == 'ATLAS_PH_UART':
                new_sensor.measurements = 'ph'
                new_sensor.location = 'Tx/Rx'
                new_sensor.interface = 'UART'
                new_sensor.baud_rate = 9600
                if GPIO.RPI_INFO['P1_REVISION'] == 3:
                    new_sensor.device_loc = "/dev/ttyS0"
                else:
                    new_sensor.device_loc = "/dev/ttyAMA0"

            # Pressure
            elif form_add_sensor.sensor.data in ['BME280',
                                                 'BMP180',
                                                 'BMP280']:
                if form_add_sensor.sensor.data == 'BME280':
                    new_sensor.measurements = 'temperature,humidity,' \
                                              'dewpoint,pressure,altitude'
                    new_sensor.location = '0x76'
                elif form_add_sensor.sensor.data in ['BMP180', 'BMP280']:
                    new_sensor.measurements = 'temperature,pressure,altitude'
                    new_sensor.location = '0x77'

            # Light
            elif form_add_sensor.sensor.data in ['BH1750', 'TSL2561', 'TSL2591']:
                new_sensor.measurements = 'lux'
                if form_add_sensor.sensor.data == 'BH1750':
                    new_sensor.location = '0x23'
                    new_sensor.resolution = 0  # 0=Low, 1=High, 2=High2
                    new_sensor.sensitivity = 69
                elif form_add_sensor.sensor.data == 'TSL2561':
                    new_sensor.location = '0x39'
                elif form_add_sensor.sensor.data == 'TSL2591':
                    new_sensor.location = '0x29'

            # Analog to Digital Converters
            elif form_add_sensor.sensor.data in ['ADS1x15', 'MCP342x']:
                new_sensor.measurements = 'voltage'
                if form_add_sensor.sensor.data == 'ADS1x15':
                    new_sensor.location = '0x48'
                    new_sensor.adc_volts_min = -4.096
                    new_sensor.adc_volts_max = 4.096
                elif form_add_sensor.sensor.data == 'MCP342x':
                    new_sensor.location = '0x68'
                    new_sensor.adc_volts_min = -2.048
                    new_sensor.adc_volts_max = 2.048

            try:
                new_sensor.save()

                display_order = csv_to_list_of_int(
                    DisplayOrder.query.first().sensor)
                DisplayOrder.query.first().sensor = add_display_order(
                    display_order, new_sensor.id)
                db.session.commit()

                flash(gettext(
                    u"%(type)s Sensor with ID %(id)s (%(uuid)s) successfully added",
                    type=form_add_sensor.sensor.data,
                    id=new_sensor.id,
                    uuid=new_sensor.unique_id),
                      "success")
            except sqlalchemy.exc.OperationalError as except_msg:
                error.append(except_msg)
            except sqlalchemy.exc.IntegrityError as except_msg:
                error.append(except_msg)
        flash_success_errors(error, action, url_for('page_routes.page_input'))
    else:
        flash_form_errors(form_add_sensor)