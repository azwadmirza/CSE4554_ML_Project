def sensor_deactivate_associated_controllers(sensor_id):
    sensor_unique_id = Sensor.query.filter(Sensor.id == sensor_id).first().unique_id
    pid = PID.query.filter(PID.is_activated == True).all()
    for each_pid in pid:
        if sensor_unique_id in each_pid.measurement:
            controller_activate_deactivate('deactivate',
                                           'PID',
                                           each_pid.id)

    lcd = LCD.query.filter(LCD.is_activated)
    for each_lcd in lcd:
        if sensor_id in [each_lcd.line_1_sensor_id,
                         each_lcd.line_2_sensor_id,
                         each_lcd.line_3_sensor_id,
                         each_lcd.line_4_sensor_id]:
            controller_activate_deactivate('deactivate',
                                           'LCD',
                                           each_lcd.id)