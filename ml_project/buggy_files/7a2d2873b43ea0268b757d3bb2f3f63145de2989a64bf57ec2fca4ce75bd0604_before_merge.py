def _parse_radius(radius):
    try:
        angle = commons.parse_radius(radius)
        # find the most appropriate unit - d, m or s
        index = min([i for (i, val) in enumerate(angle.dms) if int(val) > 0])
        unit = ('d', 'm', 's')[index]
        if unit == 'd':
            return str(int(angle.degree)) + unit
        if unit == 'm':
            sec_to_min = abs(angle.dms[2]) * u.arcsec.to(u.arcmin)
            total_min = abs(angle.dms[1]) + sec_to_min
            return str(total_min) + unit
        if unit == 's':
            return str(abs(angle.dms[2])) + unit
    except (coord.errors.UnitsError, AttributeError):
        raise ValueError("Radius specified incorrectly")