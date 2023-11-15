def has_required_pid_values(pid_id):
    pid = PID.query.filter(
        PID.id == pid_id).first()
    error = False
    if not pid.measurement:
        flash(gettext(u"A valid Measurement is required"), "error")
        error = True
    sensor_unique_id = pid.measurement.split(',')[0]
    sensor = Sensor.query.filter(
        Sensor.unique_id == sensor_unique_id).first()
    if not sensor:
        flash(gettext(u"A valid sensor is required"), "error")
        error = True
    if not pid.raise_relay_id and not pid.lower_relay_id:
        flash(gettext(u"A Raise Relay ID and/or a Lower Relay ID is "
                      "required"), "error")
        error = True
    if error:
        return redirect('/pid')