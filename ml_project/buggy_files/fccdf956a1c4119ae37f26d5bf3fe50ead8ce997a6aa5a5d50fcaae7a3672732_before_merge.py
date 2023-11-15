def page_lcd():
    """ Display LCD output settings """
    lcd = LCD.query.all()
    pid = PID.query.all()
    relay = Relay.query.all()
    sensor = Sensor.query.all()

    display_order = csv_to_list_of_int(DisplayOrder.query.first().lcd)

    form_add_lcd = flaskforms.LCDAdd()
    form_mod_lcd = flaskforms.LCDMod()

    if request.method == 'POST':
        if not flaskutils.user_has_permission('edit_controllers'):
            return redirect(url_for('general_routes.home'))

        if form_add_lcd.add.data:
            flaskutils.lcd_add(form_add_lcd.quantity.data)
        elif form_mod_lcd.save.data:
            flaskutils.lcd_mod(form_mod_lcd)
        elif form_mod_lcd.delete.data:
            flaskutils.lcd_del(form_mod_lcd.lcd_id.data)
        elif form_mod_lcd.reorder_up.data:
            flaskutils.lcd_reorder(form_mod_lcd.lcd_id.data,
                                   display_order, 'up')
        elif form_mod_lcd.reorder_down.data:
            flaskutils.lcd_reorder(form_mod_lcd.lcd_id.data,
                                   display_order, 'down')
        elif form_mod_lcd.activate.data:
            flaskutils.lcd_activate(form_mod_lcd.lcd_id.data)
        elif form_mod_lcd.deactivate.data:
            flaskutils.lcd_deactivate(form_mod_lcd.lcd_id.data)
        elif form_mod_lcd.reset_flashing.data:
            flaskutils.lcd_reset_flashing(form_mod_lcd.lcd_id.data)
        return redirect('/lcd')

    return render_template('pages/lcd.html',
                           lcd=lcd,
                           measurements=MEASUREMENTS,
                           pid=pid,
                           relay=relay,
                           sensor=sensor,
                           displayOrder=display_order,
                           form_add_lcd=form_add_lcd,
                           form_mod_lcd=form_mod_lcd)