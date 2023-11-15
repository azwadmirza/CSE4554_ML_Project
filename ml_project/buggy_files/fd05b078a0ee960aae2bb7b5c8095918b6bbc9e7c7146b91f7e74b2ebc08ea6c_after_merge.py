def page_pid():
    """ Display PID settings """
    method = Method.query.all()
    pids = PID.query.all()
    relay = Relay.query.all()
    sensor = Sensor.query.all()

    sensor_choices = flaskutils.choices_sensors(sensor)

    display_order = csv_to_list_of_int(DisplayOrder.query.first().pid)

    form_add_pid = flaskforms.PIDAdd()
    form_mod_pid_base = flaskforms.PIDModBase()
    form_mod_pid_relay = flaskforms.PIDModRelay()
    form_mod_pid_pwm = flaskforms.PIDModPWM()

    # Create list of file names from the pid_options directory
    # Used in generating the correct options for each PID
    pid_templates = []
    pid_path = os.path.join(
        INSTALL_DIRECTORY,
        'mycodo/mycodo_flask/templates/pages/pid_options')
    for (_, _, file_names) in os.walk(pid_path):
        pid_templates.extend(file_names)
        break

    if request.method == 'POST':
        if not flaskutils.user_has_permission('edit_controllers'):
            return redirect(url_for('general_routes.home'))

        form_name = request.form['form-name']
        if form_name == 'addPID':
            flaskutils.pid_add(form_add_pid)
        elif form_name == 'modPID':
            if form_mod_pid_base.save.data:
                flaskutils.pid_mod(form_mod_pid_base,
                                   form_mod_pid_pwm,
                                   form_mod_pid_relay)
            elif form_mod_pid_base.delete.data:
                flaskutils.pid_del(
                    form_mod_pid_base.pid_id.data)
            elif form_mod_pid_base.reorder_up.data:
                flaskutils.pid_reorder(
                    form_mod_pid_base.pid_id.data, display_order, 'up')
            elif form_mod_pid_base.reorder_down.data:
                flaskutils.pid_reorder(
                    form_mod_pid_base.pid_id.data, display_order, 'down')
            elif form_mod_pid_base.activate.data:
                flaskutils.pid_activate(
                    form_mod_pid_base.pid_id.data)
            elif form_mod_pid_base.deactivate.data:
                flaskutils.pid_deactivate(
                    form_mod_pid_base.pid_id.data)
            elif form_mod_pid_base.hold.data:
                flaskutils.pid_manipulate(
                    form_mod_pid_base.pid_id.data, 'Hold')
            elif form_mod_pid_base.pause.data:
                flaskutils.pid_manipulate(
                    form_mod_pid_base.pid_id.data, 'Pause')
            elif form_mod_pid_base.resume.data:
                flaskutils.pid_manipulate(
                    form_mod_pid_base.pid_id.data, 'Resume')

        return redirect('/pid')

    return render_template('pages/pid.html',
                           method=method,
                           pids=pids,
                           pid_templates=pid_templates,
                           relay=relay,
                           sensor=sensor,
                           sensor_choices=sensor_choices,
                           displayOrder=display_order,
                           form_add_pid=form_add_pid,
                           form_mod_pid_base=form_mod_pid_base,
                           form_mod_pid_pwm=form_mod_pid_pwm,
                           form_mod_pid_relay=form_mod_pid_relay)