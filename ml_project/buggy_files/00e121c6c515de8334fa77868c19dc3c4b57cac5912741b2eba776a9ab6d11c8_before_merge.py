def pid_activate(pid_id):
    if has_required_pid_values(pid_id):
        return redirect(url_for('page_routes.page_pid'))

    action = '{action} {controller}'.format(
        action=gettext(u"Actuate"),
        controller=gettext(u"PID"))
    error = []

    # Check if associated sensor is activated
    pid = PID.query.filter(
        PID.id == pid_id).first()
    sensor = Sensor.query.filter(
        Sensor.id == pid.sensor_id).first()

    if not sensor.is_activated:
        error.append(gettext(
            u"Cannot activate PID controller if the associated sensor "
            u"controller is inactive"))

    if ((pid.direction == 'both' and not (pid.lower_relay_id and pid.raise_relay_id)) or
                (pid.direction == 'lower' and not pid.lower_relay_id) or
                (pid.direction == 'raise' and not pid.raise_relay_id)):
        error.append(gettext(
            u"Cannot activate PID controller if raise and/or lower relay IDs "
            u"are not selected"))

    if not error:
        # Signal the duration method can run because it's been
        # properly initiated (non-power failure)
        mod_method = Method.query.filter(
            Method.id == pid.method_id).first()
        if mod_method and mod_method.method_type == 'Duration':
            mod_method.start_time = 'Ready'
            db.session.commit()

        time.sleep(1)
        controller_activate_deactivate('activate',
                                       'PID',
                                       pid_id)

    flash_success_errors(error, action, url_for('page_routes.page_pid'))