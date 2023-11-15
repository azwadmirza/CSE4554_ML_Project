def import_event(vevent, collection, locale, batch, random_uid):
    """import one event into collection, let user choose the collection"""

    # print all sub-events
    for sub_event in vevent:
        if not batch:
            event = Event.fromVEvents(
                [sub_event], calendar=collection.default_calendar_name, locale=locale)
            echo(event.event_description)

    # get the calendar to insert into
    if batch or len(collection.writable_names) == 1:
        calendar_name = collection.writable_names[0]
    else:
        choice = list()
        for num, name in enumerate(collection.writable_names):
            choice.append('{}({})'.format(name, num))
        choice = ', '.join(choice)
        while True:
            value = prompt('Which calendar do you want to import to? \n'
                           '{}'.format(choice), default=collection.default_calendar_name)
            try:
                number = int(value)
                calendar_name = collection.writable_names[number]
                break
            except (ValueError, IndexError):
                matches = filter(lambda x: x.startswith(value), collection.writable_names)
                if len(matches) == 1:
                    calendar_name = matches[0]
                    break
            echo('invalid choice')

    if batch or confirm("Do you want to import this event into `{}`?"
                        "".format(calendar_name)):
        ics = aux.ics_from_list(vevent, random_uid)
        try:
            collection.new(
                Item(ics.to_ical().decode('utf-8')),
                collection=calendar_name)
        except DuplicateUid:
            if batch or confirm("An event with the same UID already exists. "
                                "Do you want to update it?"):
                collection.force_update(
                    Item(ics.to_ical().decode('utf-8')),
                    collection=calendar_name)
            else:
                logger.warn("Not importing event with UID `{}`".format(event.uid))