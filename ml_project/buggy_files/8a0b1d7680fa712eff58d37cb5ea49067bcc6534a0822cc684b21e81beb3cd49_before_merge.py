def _changes(name,
             uid=None,
             gid=None,
             groups=None,
             optional_groups=None,
             remove_groups=True,
             home=None,
             createhome=True,
             password=None,
             enforce_password=True,
             empty_password=False,
             shell=None,
             fullname='',
             roomnumber='',
             workphone='',
             homephone='',
             loginclass=None,
             date=0,
             mindays=0,
             maxdays=999999,
             inactdays=0,
             warndays=7,
             expire=-1,
             win_homedrive=None,
             win_profile=None,
             win_logonscript=None,
             win_description=None):
    '''
    Return a dict of the changes required for a user if the user is present,
    otherwise return False.

    Updated in 2015.8.0 to include support for windows homedrive, profile,
    logonscript, and description fields.

    Updated in 2014.7.0 to include support for shadow attributes, all
    attributes supported as integers only.
    '''

    if 'shadow.info' in __salt__:
        lshad = __salt__['shadow.info'](name)

    lusr = __salt__['user.info'](name)
    if not lusr:
        return False

    change = {}
    if groups is None:
        groups = lusr['groups']
    wanted_groups = sorted(set((groups or []) + (optional_groups or [])))
    if uid and lusr['uid'] != uid:
        change['uid'] = uid
    if gid is not None and lusr['gid'] not in (gid, __salt__['file.group_to_gid'](gid)):
        change['gid'] = gid
    default_grp = __salt__['file.gid_to_group'](
        gid if gid is not None else lusr['gid']
    )
    # remove the default group from the list for comparison purposes
    if default_grp in lusr['groups']:
        lusr['groups'].remove(default_grp)
    if name in lusr['groups'] and name not in wanted_groups:
        lusr['groups'].remove(name)
    # remove default group from wanted_groups, as this requirement is
    # already met
    if default_grp in wanted_groups:
        wanted_groups.remove(default_grp)
    if _group_changes(lusr['groups'], wanted_groups, remove_groups):
        change['groups'] = wanted_groups
    if home and lusr['home'] != home:
        change['home'] = home
    if createhome:
        newhome = home if home else lusr['home']
        if newhome is not None and not os.path.isdir(newhome):
            change['homeDoesNotExist'] = newhome
    if shell and lusr['shell'] != shell:
        change['shell'] = shell
    if 'shadow.info' in __salt__ and 'shadow.default_hash' in __salt__:
        if password:
            default_hash = __salt__['shadow.default_hash']()
            if lshad['passwd'] == default_hash \
                    or lshad['passwd'] != default_hash and enforce_password:
                if lshad['passwd'] != password:
                    change['passwd'] = password
        if date and date is not 0 and lshad['lstchg'] != date:
            change['date'] = date
        if mindays and mindays is not 0 and lshad['min'] != mindays:
            change['mindays'] = mindays
        if maxdays and maxdays is not 999999 and lshad['max'] != maxdays:
            change['maxdays'] = maxdays
        if inactdays and inactdays is not 0 and lshad['inact'] != inactdays:
            change['inactdays'] = inactdays
        if warndays and warndays is not 7 and lshad['warn'] != warndays:
            change['warndays'] = warndays
        if expire and expire is not -1 and lshad['expire'] != expire:
            change['expire'] = expire
    elif 'shadow.info' in __salt__ and salt.utils.is_windows():
        if expire and expire is not -1 and salt.utils.date_format(lshad['expire']) != salt.utils.date_format(expire):
            change['expire'] = expire

    # GECOS fields
    if isinstance(fullname, string_types):
        fullname = sdecode(fullname)
    if isinstance(lusr['fullname'], string_types):
        lusr['fullname'] = sdecode(lusr['fullname'])
    if fullname is not None and lusr['fullname'] != fullname:
        change['fullname'] = fullname
    if win_homedrive and lusr['homedrive'] != win_homedrive:
        change['homedrive'] = win_homedrive
    if win_profile and lusr['profile'] != win_profile:
        change['profile'] = win_profile
    if win_logonscript and lusr['logonscript'] != win_logonscript:
        change['logonscript'] = win_logonscript
    if win_description and lusr['description'] != win_description:
        change['description'] = win_description

    # MacOS doesn't have full GECOS support, so check for the "ch" functions
    # and ignore these parameters if these functions do not exist.
    if 'user.chroomnumber' in __salt__ \
            and roomnumber is not None \
            and lusr['roomnumber'] != roomnumber:
        change['roomnumber'] = roomnumber
    if 'user.chworkphone' in __salt__ \
            and workphone is not None \
            and lusr['workphone'] != workphone:
        change['workphone'] = workphone
    if 'user.chhomephone' in __salt__ \
            and homephone is not None \
            and lusr['homephone'] != homephone:
        change['homephone'] = homephone
    # OpenBSD/FreeBSD login class
    if __grains__['kernel'] in ('OpenBSD', 'FreeBSD'):
        if loginclass:
            if __salt__['user.get_loginclass'](name) != loginclass:
                change['loginclass'] = loginclass

    return change