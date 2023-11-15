def pid_mod(form_mod_pid_base, form_mod_pid_pwm, form_mod_pid_relay):
    action = u'{action} {controller}'.format(
        action=gettext(u"Modify"),
        controller=gettext(u"PID"))
    error = []

    if not form_mod_pid_base.validate():
        flash_form_errors(form_mod_pid_base)

    try:
        sensor = Sensor.query.filter(
            Sensor.id == form_mod_pid_base.sensor_id.data).first()
        if not sensor:
            error.append(gettext(u"A valid sensor ID is required"))
        elif (sensor.device != 'LinuxCommand' and
                sensor.device not in MEASUREMENTS):
            error.append(gettext(u"Invalid sensor"))
        elif (sensor.device != 'LinuxCommand' and
                form_mod_pid_base.measurement.data not in MEASUREMENTS[sensor.device]):
            error.append(gettext(
                u"Select a Measure Type that is compatible with the "
                u"chosen sensor"))
        if not error:
            mod_pid = PID.query.filter(
                PID.id == form_mod_pid_base.pid_id.data).first()
            mod_pid.name = form_mod_pid_base.name.data
            if form_mod_pid_base.sensor_id.data:
                mod_pid.sensor_id = form_mod_pid_base.sensor_id.data
            else:
                mod_pid.sensor_id = None
            mod_pid.measurement = form_mod_pid_base.measurement.data
            mod_pid.direction = form_mod_pid_base.direction.data
            mod_pid.period = form_mod_pid_base.period.data
            mod_pid.max_measure_age = form_mod_pid_base.max_measure_age.data
            mod_pid.setpoint = form_mod_pid_base.setpoint.data
            mod_pid.p = form_mod_pid_base.k_p.data
            mod_pid.i = form_mod_pid_base.k_i.data
            mod_pid.d = form_mod_pid_base.k_d.data
            mod_pid.integrator_min = form_mod_pid_base.integrator_max.data
            mod_pid.integrator_max = form_mod_pid_base.integrator_min.data
            if form_mod_pid_base.method_id.data:
                mod_pid.method_id = form_mod_pid_base.method_id.data
            else:
                mod_pid.method_id = None

            if mod_pid.pid_type == 'relay':
                if not form_mod_pid_relay.validate():
                    flash_form_errors(form_mod_pid_relay)
                else:
                    if form_mod_pid_relay.raise_relay_id.data:
                        mod_pid.raise_relay_id = form_mod_pid_relay.raise_relay_id.data
                    else:
                        mod_pid.raise_relay_id = None
                    mod_pid.raise_min_duration = form_mod_pid_relay.raise_min_duration.data
                    mod_pid.raise_max_duration = form_mod_pid_relay.raise_max_duration.data
                    mod_pid.raise_min_off_duration = form_mod_pid_relay.raise_min_off_duration.data
                    if form_mod_pid_relay.lower_relay_id.data:
                        mod_pid.lower_relay_id = form_mod_pid_relay.lower_relay_id.data
                    else:
                        mod_pid.lower_relay_id = None
                    mod_pid.lower_min_duration = form_mod_pid_relay.lower_min_duration.data
                    mod_pid.lower_max_duration = form_mod_pid_relay.lower_max_duration.data
                    mod_pid.lower_min_off_duration = form_mod_pid_relay.lower_min_off_duration.data

            elif mod_pid.pid_type == 'pwm':
                if not form_mod_pid_pwm.validate():
                    flash_form_errors(form_mod_pid_pwm)
                else:
                    if form_mod_pid_relay.raise_relay_id.data:
                        mod_pid.raise_relay_id = form_mod_pid_pwm.raise_relay_id.data
                    else:
                        mod_pid.raise_relay_id = None
                    if form_mod_pid_relay.lower_relay_id.data:
                        mod_pid.lower_relay_id = form_mod_pid_pwm.lower_relay_id.data
                    else:
                        mod_pid.lower_relay_id = None
                    mod_pid.raise_min_duration = form_mod_pid_pwm.raise_min_duty_cycle.data
                    mod_pid.raise_max_duration = form_mod_pid_pwm.raise_max_duty_cycle.data
                    mod_pid.lower_min_duration = form_mod_pid_pwm.lower_min_duty_cycle.data
                    mod_pid.lower_max_duration = form_mod_pid_pwm.lower_max_duty_cycle.data

            db.session.commit()
            # If the controller is active or paused, refresh variables in thread
            if mod_pid.is_activated:
                control = DaemonControl()
                return_value = control.pid_mod(form_mod_pid_base.pid_id.data)
                flash(gettext(
                    u"PID Controller settings refresh response: %(resp)s",
                    resp=return_value), "success")
    except Exception as except_msg:
        error.append(except_msg)
    flash_success_errors(error, action, url_for('page_routes.page_pid'))