def get_expected_titles(show_list):
    """Return expected titles to be used by guessit.

    It iterates over user's show list and only returns a regex for titles that contains numbers
    (since they can confuse guessit).

    :param show_list:
    :type show_list: list of sickbeard.tv.TVShow
    :return:
    :rtype: list of str
    """
    expected_titles = list(fixed_expected_titles)
    for show in show_list:
        names = [show.name] + show.exceptions
        for name in names:
            match = series_re.match(name)
            if not match:
                continue

            series, year, _ = match.groups()
            if year and not valid_year(int(year)):
                series = name

            if not any([char.isdigit() for char in series]):
                continue

            if not any([char.isalpha() for char in series]):
                # if no alpha chars then add series name 'as-is'
                expected_titles.append(series)

            # (?<![^/\\]) means -> it matches nothing but path separators and dot (negative lookbehind)
            fmt = r're:\b{name}\b' if show.is_anime else r're:(?<![^/\\\.]){name}\b'
            expected_titles.append(fmt.format(name=prepare(series)))

    return normalize(expected_titles)