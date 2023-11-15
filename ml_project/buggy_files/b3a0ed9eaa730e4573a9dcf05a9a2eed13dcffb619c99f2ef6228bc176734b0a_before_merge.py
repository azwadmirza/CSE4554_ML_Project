def delete_instance(vevent, instance):
    """remove a recurrence instance from a VEVENT's RRDATE list

    :type vevent: icalendar.cal.Event
    :type instance: datetime.datetime
    """

    if 'RDATE' in vevent and 'RRULE' in vevent:
        # TODO check where this instance is coming from and only call the
        # appropriate function
        _add_exdate(vevent, instance)
        _remove_instance(vevent, instance)
    elif 'RRULE' in vevent:
        _add_exdate(vevent, instance)
    elif 'RDATE' in vevent:
        _remove_instance(vevent, instance)