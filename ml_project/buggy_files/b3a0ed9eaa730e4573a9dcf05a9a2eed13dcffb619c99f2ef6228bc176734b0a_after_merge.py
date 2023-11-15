def delete_instance(vevent, instance):
    """remove a recurrence instance from a VEVENT's RRDATE list or add it
    to the EXDATE list

    :type vevent: icalendar.cal.Event
    :type instance: datetime.datetime
    """
    # TODO check where this instance is coming from and only call the
    # appropriate function
    if 'RRULE' in vevent:
        exdates = _get_all_properties(vevent, 'EXDATE')
        exdates += [instance]
        vevent.pop('EXDATE')
        vevent.add('EXDATE', exdates)
    if 'RDATE' in vevent:
        rdates = [one for one in _get_all_properties(vevent, 'RDATE') if one != instance]
        vevent.pop('RDATE')
        if rdates != []:
            vevent.add('RDATE', rdates)