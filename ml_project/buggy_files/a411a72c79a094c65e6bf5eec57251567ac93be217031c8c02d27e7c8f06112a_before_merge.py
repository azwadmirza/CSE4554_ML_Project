def sensor_deactivate_associated_controllers(sensor_id):
    pid = (PID.query
           .filter(PID.sensor_id == sensor_id)
           .filter(PID.is_activated == True)
           ).all()
    if pid:
        for each_pid in pid:
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