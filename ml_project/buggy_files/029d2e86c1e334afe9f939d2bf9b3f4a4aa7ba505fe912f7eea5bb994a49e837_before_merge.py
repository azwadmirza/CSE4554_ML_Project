def show_bug(bot, trigger, match=None):
    """Show information about a Bugzilla bug."""
    match = match or trigger
    domain = match.group(1)
    if domain not in bot.config.bugzilla.domains:
        return
    url = 'https://%s%sctype=xml&%s' % match.groups()
    data = web.get(url, dont_decode=True)
    bug = xmltodict.parse(data).get('bugzilla').get('bug')
    error = bug.get('@error', None)  # error="NotPermitted"

    if error:
        LOGGER.warning('Bugzilla error: %s', error)
        return

    message = ('[BUGZILLA] %s | Product: %s | Component: %s | Version: %s | ' +
               'Importance: %s |  Status: %s | Assigned to: %s | ' +
               'Reported: %s | Modified: %s')

    resolution = bug.get('resolution')
    if resolution is not None:
        status = bug.get('bug_status') + ' ' + resolution
    else:
        status = bug.get('bug_status')

    assigned_to = bug.get('assigned_to')
    if isinstance(assigned_to, dict):
        assigned_to = assigned_to.get('@name')

    message = message % (
        bug.get('short_desc'), bug.get('product'),
        bug.get('component'), bug.get('version'),
        (bug.get('priority') + ' ' + bug.get('bug_severity')),
        status, assigned_to, bug.get('creation_ts'),
        bug.get('delta_ts'))
    bot.say(message)