def sensors_temperatures():
    """Return hardware (CPU and others) temperatures as a dict
    including hardware name, label, current, max and critical
    temperatures.

    Implementation notes:
    - /sys/class/hwmon looks like the most recent interface to
      retrieve this info, and this implementation relies on it
      only (old distros will probably use something else)
    - lm-sensors on Ubuntu 16.04 relies on /sys/class/hwmon
    - /sys/class/thermal/thermal_zone* is another one but it's more
      difficult to parse
    """
    ret = collections.defaultdict(list)
    basenames = glob.glob('/sys/class/hwmon/hwmon*/temp*_*')
    # CentOS has an intermediate /device directory:
    # https://github.com/giampaolo/psutil/issues/971
    # https://github.com/nicolargo/glances/issues/1060
    basenames.extend(glob.glob('/sys/class/hwmon/hwmon*/device/temp*_*'))
    basenames = sorted(set([x.split('_')[0] for x in basenames]))

    for base in basenames:
        try:
            current = float(cat(base + '_input')) / 1000.0
        except (IOError, OSError) as err:
            # A lot of things can go wrong here, so let's just skip the
            # whole entry.
            # https://github.com/giampaolo/psutil/issues/1009
            # https://github.com/giampaolo/psutil/issues/1101
            # https://github.com/giampaolo/psutil/issues/1129
            warnings.warn("ignoring %r" % err, RuntimeWarning)
            continue

        unit_name = cat(os.path.join(os.path.dirname(base), 'name'),
                        binary=False)
        high = cat(base + '_max', fallback=None)
        critical = cat(base + '_crit', fallback=None)
        label = cat(base + '_label', fallback='', binary=False)

        if high is not None:
            high = float(high) / 1000.0
        if critical is not None:
            critical = float(critical) / 1000.0

        ret[unit_name].append((label, current, high, critical))

    return ret