def create_script(typeclass=None, key=None, obj=None, account=None, locks=None,
                  interval=None, start_delay=None, repeats=None,
                  persistent=None, autostart=True, report_to=None, desc=None,
                  tags=None, attributes=None):
    """
    Create a new script. All scripts are a combination of a database
    object that communicates with the database, and an typeclass that
    'decorates' the database object into being different types of
    scripts.  It's behaviour is similar to the game objects except
    scripts has a time component and are more limited in scope.

    Kwargs:
        typeclass (class or str): Class or python path to a typeclass.
        key (str): Name of the new object. If not set, a name of
            #dbref will be set.
        obj (Object): The entity on which this Script sits. If this
            is `None`, we are creating a "global" script.
        account (Account): The account on which this Script sits. It is
            exclusiv to `obj`.
        locks (str): one or more lockstrings, separated by semicolons.
        interval (int): The triggering interval for this Script, in
            seconds. If unset, the Script will not have a timing
            component.
        start_delay (bool): If `True`, will wait `interval` seconds
            before triggering the first time.
        repeats (int): The number of times to trigger before stopping.
            If unset, will repeat indefinitely.
        persistent (bool): If this Script survives a server shutdown
            or not (all Scripts will survive a reload).
        autostart (bool): If this Script will start immediately when
            created or if the `start` method must be called explicitly.
        report_to (Object): The object to return error messages to.
        desc (str): Optional description of script
        tags (list): List of tags or tuples (tag, category).
        attributes (list): List if tuples (key, value) or (key, value, category)
           (key, value, lockstring) or (key, value, lockstring, default_access).

    See evennia.scripts.manager for methods to manipulate existing
    scripts in the database.

    """
    global _ScriptDB
    if not _ScriptDB:
        from evennia.scripts.models import ScriptDB as _ScriptDB

    typeclass = typeclass if typeclass else settings.BASE_SCRIPT_TYPECLASS

    if isinstance(typeclass, basestring):
        # a path is given. Load the actual typeclass
        typeclass = class_from_module(typeclass, settings.TYPECLASS_PATHS)

    # validate input
    kwarg = {}
    if key:
        kwarg["db_key"] = key
    if account:
        kwarg["db_account"] = dbid_to_obj(account, _AccountDB)
    if obj:
        kwarg["db_obj"] = dbid_to_obj(obj, _ObjectDB)
    if interval:
        kwarg["db_interval"] = interval
    if start_delay:
        kwarg["db_start_delay"] = start_delay
    if repeats:
        kwarg["db_repeats"] = repeats
    if persistent:
        kwarg["db_persistent"] = persistent
    if desc:
        kwarg["db_desc"] = desc
    tags = make_iter(tags) if tags is not None else None
    attributes = make_iter(attributes) if attributes is not None else None

    # create new instance
    new_script = typeclass(**kwarg)

    # store the call signature for the signal
    new_script._createdict = dict(key=key, obj=obj, account=account, locks=locks, interval=interval,
                                  start_delay=start_delay, repeats=repeats, persistent=persistent,
                                  autostart=autostart, report_to=report_to, desc=desc,
                                  tags=tags, attributes=attributes)
    # this will trigger the save signal which in turn calls the
    # at_first_save hook on the typeclass, where the _createdict
    # can be used.
    new_script.save()

    if not new_script.id:
        # this happens in the case of having a repeating script with `repeats=1` and
        # `start_delay=False` - the script will run once and immediately stop before save is over.
        return None

    return new_script