def has_required_pid_values(pid_id):
    pid = PID.query.filter(
        PID.id == pid_id).first()
    error = False
    # TODO: Add more settings-checks before allowing controller to be activated
    if not pid.sensor_id:
        flash(gettext(u"A valid sensor is required"), "error")
        error = True
    if not pid.measurement:
        flash(gettext(u"A valid Measure Type is required"), "error")
        error = True
    if not pid.raise_relay_id and not pid.lower_relay_id:
        flash(gettext(u"A Raise Relay ID and/or a Lower Relay ID is "
                      "required"), "error")
        error = True
    if error:
        return redirect('/pid')