def date_in_range(date_range, date, debug=False, now=None):
    """Check if date is in the range specified.

    Format:
    * comma-separated clauses (AND)
    * clause: attribute comparison_operator value (spaces optional)
        * attribute: year, month, day, hour, month, second, weekday, isoweekday
          or empty for full datetime
        * comparison_operator: == != <= >= < >
        * value: integer, 'now', 'today', or dateutil-compatible date input

    The optional `now` parameter can be used to provide a specific `now`/`today` value
    (if none is provided, datetime.datetime.now()/datetime.date.today() is used).
    """
    out = True

    for item in date_range.split(','):
        attribute, comparison_operator, value = CLAUSE.match(
            item.strip()).groups()
        if attribute in ('weekday', 'isoweekday'):
            left = getattr(date, attribute)()
            right = int(value)
        elif value == 'now':
            left = date
            right = now or datetime.datetime.now()
        elif value == 'today':
            left = date.date() if isinstance(date, datetime.datetime) else date
            if now:
                right = now.date() if isinstance(now, datetime.datetime) else now
            else:
                right = datetime.date.today()
        elif attribute:
            left = getattr(date, attribute)
            right = int(value)
        else:
            left = date
            right = dateutil.parser.parse(value)
        if debug:  # pragma: no cover
            print("    <{0} {1} {2}>".format(left, comparison_operator, right))
        out = out and OPERATORS[comparison_operator](left, right)
    return out