def _period_alias_dictionary():
    """
    Build freq alias dictionary to support freqs from original c_dates.c file
    of the scikits.timeseries library.
    """
    alias_dict = {}

    M_aliases = ["M", "MTH", "MONTH", "MONTHLY"]
    B_aliases = ["B", "BUS", "BUSINESS", "BUSINESSLY", "WEEKDAY"]
    D_aliases = ["D", "DAY", "DLY", "DAILY"]
    H_aliases = ["H", "HR", "HOUR", "HRLY", "HOURLY"]
    T_aliases = ["T", "MIN", "MINUTE", "MINUTELY"]
    S_aliases = ["S", "SEC", "SECOND", "SECONDLY"]
    L_aliases = ["L", "ms", "MILLISECOND", "MILLISECONDLY"]
    U_aliases = ["U", "US", "MICROSECOND", "MICROSECONDLY"]
    N_aliases = ["N", "NS", "NANOSECOND", "NANOSECONDLY"]

    for k in M_aliases:
        alias_dict[k] = 'M'

    for k in B_aliases:
        alias_dict[k] = 'B'

    for k in D_aliases:
        alias_dict[k] = 'D'

    for k in H_aliases:
        alias_dict[k] = 'H'

    for k in T_aliases:
        alias_dict[k] = 'T'

    for k in S_aliases:
        alias_dict[k] = 'S'

    for k in L_aliases:
        alias_dict[k] = 'L'

    for k in U_aliases:
        alias_dict[k] = 'U'

    for k in N_aliases:
        alias_dict[k] = 'N'

    A_prefixes = ["A", "Y", "ANN", "ANNUAL", "ANNUALLY", "YR", "YEAR",
                  "YEARLY"]

    Q_prefixes = ["Q", "QTR", "QUARTER", "QUARTERLY", "Q-E",
                  "QTR-E", "QUARTER-E", "QUARTERLY-E"]

    month_names = [
        ["DEC", "DECEMBER"],
        ["JAN", "JANUARY"],
        ["FEB", "FEBRUARY"],
        ["MAR", "MARCH"],
        ["APR", "APRIL"],
        ["MAY", "MAY"],
        ["JUN", "JUNE"],
        ["JUL", "JULY"],
        ["AUG", "AUGUST"],
        ["SEP", "SEPTEMBER"],
        ["OCT", "OCTOBER"],
        ["NOV", "NOVEMBER"]]

    seps = ["@", "-"]

    for k in A_prefixes:
        alias_dict[k] = 'A'
        for m_tup in month_names:
            for sep in seps:
                m1, m2 = m_tup
                alias_dict[k + sep + m1] = 'A-' + m1
                alias_dict[k + sep + m2] = 'A-' + m1

    for k in Q_prefixes:
        alias_dict[k] = 'Q'
        for m_tup in month_names:
            for sep in seps:
                m1, m2 = m_tup
                alias_dict[k + sep + m1] = 'Q-' + m1
                alias_dict[k + sep + m2] = 'Q-' + m1

    W_prefixes = ["W", "WK", "WEEK", "WEEKLY"]

    day_names = [
        ["SUN", "SUNDAY"],
        ["MON", "MONDAY"],
        ["TUE", "TUESDAY"],
        ["WED", "WEDNESDAY"],
        ["THU", "THURSDAY"],
        ["FRI", "FRIDAY"],
        ["SAT", "SATURDAY"]]

    for k in W_prefixes:
        alias_dict[k] = 'W'
        for d_tup in day_names:
            for sep in ["@", "-"]:
                d1, d2 = d_tup
                alias_dict[k + sep + d1] = 'W-' + d1
                alias_dict[k + sep + d2] = 'W-' + d1

    return alias_dict