def show_bug(willie, trigger):
    """Show information about a Bugzilla bug."""
    domain = trigger.group(1)
    if domain not in willie.config.bugzilla.get_list('domains'):
        return
    url = 'https://%s%sctype=xml&%s' % trigger.groups()
    data = web.get(url)
    bug = etree.fromstring(data).find('bug')

    message = ('[BUGZILLA] %s | Product: %s | Component: %s | Version: %s | ' +
               'Importance: %s |  Status: %s | Assigned to: %s | ' +
               'Reported: %s | Modified: %s')

    resolution = bug.find('resolution')
    if resolution is not None and resolution.text:
        status = bug.find('bug_status').text + ' ' + resolution.text
    else:
        status = bug.find('bug_status').text

    message = message % (
        bug.find('short_desc').text, bug.find('product').text,
        bug.find('component').text, bug.find('version').text,
        (bug.find('priority').text + ' ' + bug.find('bug_severity').text),
        status, bug.find('assigned_to').text, bug.find('creation_ts').text,
        bug.find('delta_ts').text)
    willie.say(message)