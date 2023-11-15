def create(kwargs):
    """
    Create a new authority.

    :return:
    """

    issuer = plugins.get(kwargs.get('pluginName'))

    kwargs['creator'] = g.current_user.email
    cert_body, intermediate, issuer_roles = issuer.create_authority(kwargs)

    cert = Certificate(cert_body, chain=intermediate)
    cert.owner = kwargs['ownerEmail']

    if kwargs['caType'] == 'subca':
        cert.description = "This is the ROOT certificate for the {0} sub certificate authority the parent \
                                authority is {1}.".format(kwargs.get('caName'), kwargs.get('caParent'))
    else:
        cert.description = "This is the ROOT certificate for the {0} certificate authority.".format(
            kwargs.get('caName')
        )

    cert.user = g.current_user

    cert.notifications = notification_service.create_default_expiration_notifications(
        'DEFAULT_SECURITY',
        current_app.config.get('LEMUR_SECURITY_TEAM_EMAIL')
    )

    # we create and attach any roles that the issuer gives us
    role_objs = []
    for r in issuer_roles:

        role = role_service.create(
            r['name'],
            password=r['password'],
            description="{0} auto generated role".format(kwargs.get('pluginName')),
            username=r['username'])

        # the user creating the authority should be able to administer it
        if role.username == 'admin':
            g.current_user.roles.append(role)

        role_objs.append(role)

    authority = Authority(
        kwargs.get('caName'),
        kwargs['ownerEmail'],
        kwargs['pluginName'],
        cert_body,
        description=kwargs['caDescription'],
        chain=intermediate,
        roles=role_objs
    )

    database.update(cert)
    authority = database.create(authority)

    # the owning dl or role should have this authority associated with it
    owner_role = role_service.get_by_name(kwargs['ownerEmail'])

    if not owner_role:
        owner_role = role_service.create(kwargs['ownerEmail'])

    owner_role.authority = authority

    g.current_user.authorities.append(authority)

    return authority