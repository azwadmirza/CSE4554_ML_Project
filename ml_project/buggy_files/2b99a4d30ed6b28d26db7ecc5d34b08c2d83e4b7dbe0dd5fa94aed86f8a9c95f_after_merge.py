def post_login_handler(sender, request, user, **kwargs):
    '''
    Signal handler for setting user language and
    migrating profile if needed.
    '''

    # Warning about setting password
    if (getattr(user, 'backend', '').endswith('.EmailAuth') and
            not user.has_usable_password()):
        request.session['show_set_password'] = True

    # Ensure user has a profile
    profile = Profile.objects.get_or_create(user=user)[0]

    # Migrate django-registration based verification to python-social-auth
    if (user.has_usable_password() and user.email and
            not user.social_auth.filter(provider='email').exists()):
        social = user.social_auth.create(
            provider='email',
            uid=user.email,
        )
        VerifiedEmail.objects.create(
            social=social,
            email=user.email,
        )

    # Set language for session based on preferences
    set_lang(request, profile)