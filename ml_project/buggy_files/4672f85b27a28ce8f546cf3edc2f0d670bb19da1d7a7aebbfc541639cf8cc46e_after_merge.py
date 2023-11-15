def get_fpath(bot, trigger, channel=None):
    """
    Returns a string corresponding to the path to the file where the message
    currently being handled should be logged.
    """
    basedir = os.path.expanduser(bot.config.chanlogs.dir)
    channel = channel or trigger.sender
    channel = channel.lstrip("#")
    channel = BAD_CHARS.sub('__')

    dt = datetime.utcnow()
    if not bot.config.chanlogs.microseconds:
        dt = dt.replace(microsecond=0)
    if bot.config.chanlogs.by_day:
        fname = "{channel}-{date}.log".format(channel=channel, date=dt.date().isoformat())
    else:
        fname = "{channel}.log".format(channel=channel)
    return os.path.join(basedir, fname)