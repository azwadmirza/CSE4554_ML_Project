def webclient_options(session, *args, **kwargs):
    """
    Handles retrieving and changing of options related to the webclient.

    If kwargs is empty (or contains just a "cmdid"), the saved options will be
    sent back to the session.
    A monitor handler will be created to inform the client of any future options
    that changes.

    If kwargs is not empty, the key/values stored in there will be persisted
    to the account object.

    Kwargs:
        <option name>: an option to save
    """
    account = session.account

    clientoptions = account.db._saved_webclient_options
    if not clientoptions:
        # No saved options for this account, copy and save the default.
        account.db._saved_webclient_options = settings.WEBCLIENT_OPTIONS.copy()
        # Get the _SaverDict created by the database.
        clientoptions = account.db._saved_webclient_options

    # The webclient adds a cmdid to every kwargs, but we don't need it.
    try:
        del kwargs["cmdid"]
    except KeyError:
        pass

    if not kwargs:
        # No kwargs: we are getting the stored options
        # Convert clientoptions to regular dict for sending.
        session.msg(webclient_options=dict(clientoptions))

        # Create a monitor. If a monitor already exists then it will replace
        # the previous one since it would use the same idstring
        from evennia.scripts.monitorhandler import MONITOR_HANDLER
        MONITOR_HANDLER.add(account, "_saved_webclient_options",
                            _on_webclient_options_change,
                            idstring=session.sessid, persistent=False,
                            session=session)
    else:
        # kwargs provided: persist them to the account object
        for key, value in kwargs.iteritems():
            clientoptions[key] = value