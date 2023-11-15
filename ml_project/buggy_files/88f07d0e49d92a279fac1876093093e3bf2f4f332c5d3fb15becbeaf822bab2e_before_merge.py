def createuser(email, password, superuser, no_password, no_input, force_update):
    "Create a new user."
    if not no_input:
        if not email:
            email = _get_email()

        if not (password or no_password):
            password = _get_password()

        if superuser is None:
            superuser = _get_superuser()

    if superuser is None:
        superuser = False

    if not email:
        raise click.ClickException("Invalid or missing email address.")

    # TODO(mattrobenolt): Accept password over stdin?
    if not no_password and not password:
        raise click.ClickException("No password set and --no-password not passed.")

    from sentry import roles
    from sentry.models import User
    from django.conf import settings

    user = User(
        email=email, username=email, is_superuser=superuser, is_staff=superuser, is_active=True
    )

    if password:
        user.set_password(password)

    if User.objects.filter(username=email).exists():
        if force_update:
            user.save(force_update=force_update)
            click.echo(f"User updated: {email}")
        else:
            click.echo(f"User: {email} exists, use --force-update to force")
            sys.exit(3)
    else:
        user.save()
        click.echo(f"User created: {email}")

        # TODO(dcramer): kill this when we improve flows
        if settings.SENTRY_SINGLE_ORGANIZATION:
            from sentry.models import Organization, OrganizationMember, OrganizationMemberTeam, Team

            org = Organization.get_default()
            if superuser:
                role = roles.get_top_dog().id
            else:
                role = org.default_role
            member = OrganizationMember.objects.create(organization=org, user=user, role=role)

            # if we've only got a single team let's go ahead and give
            # access to that team as its likely the desired outcome
            teams = list(Team.objects.filter(organization=org)[0:2])
            if len(teams) == 1:
                OrganizationMemberTeam.objects.create(team=teams[0], organizationmember=member)
            click.echo(f"Added to organization: {org.slug}")