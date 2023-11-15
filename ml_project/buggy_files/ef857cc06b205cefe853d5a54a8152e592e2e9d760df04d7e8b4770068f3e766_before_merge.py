def add_bot_backend(request, user_profile, full_name_raw=REQ("full_name"), short_name_raw=REQ("short_name"),
                    bot_type=REQ(validator=check_int, default=UserProfile.DEFAULT_BOT),
                    payload_url=REQ(validator=check_url, default=""),
                    service_name=REQ(default=None),
                    interface_type=REQ(validator=check_int, default=Service.GENERIC),
                    default_sending_stream_name=REQ('default_sending_stream', default=None),
                    default_events_register_stream_name=REQ('default_events_register_stream', default=None),
                    default_all_public_streams=REQ(validator=check_bool, default=None)):
    # type: (HttpRequest, UserProfile, Text, Text, int, Optional[Text], Optional[Text], int, Optional[Text], Optional[Text], Optional[bool]) -> HttpResponse
    short_name = check_short_name(short_name_raw)
    service_name = service_name or short_name
    short_name += "-bot"
    full_name = check_full_name(full_name_raw)
    email = '%s@%s' % (short_name, user_profile.realm.get_bot_domain())
    form = CreateUserForm({'full_name': full_name, 'email': email})

    if bot_type == UserProfile.EMBEDDED_BOT:
        if not settings.EMBEDDED_BOTS_ENABLED:
            return json_error(_("Embedded bots are not enabled."))
        if service_name not in [bot.name for bot in EMBEDDED_BOTS]:
            return json_error(_("Invalid embedded bot name."))

    if not form.is_valid():
        # We validate client-side as well
        return json_error(_('Bad name or username'))
    try:
        get_user(email, user_profile.realm)
        return json_error(_("Username already in use"))
    except UserProfile.DoesNotExist:
        pass
    check_valid_bot_type(bot_type)
    check_valid_interface_type(interface_type)

    if len(request.FILES) == 0:
        avatar_source = UserProfile.AVATAR_FROM_GRAVATAR
    elif len(request.FILES) != 1:
        return json_error(_("You may only upload one file at a time"))
    else:
        avatar_source = UserProfile.AVATAR_FROM_USER

    default_sending_stream = None
    if default_sending_stream_name is not None:
        (default_sending_stream, ignored_rec, ignored_sub) = access_stream_by_name(
            user_profile, default_sending_stream_name)

    default_events_register_stream = None
    if default_events_register_stream_name is not None:
        (default_events_register_stream, ignored_rec, ignored_sub) = access_stream_by_name(
            user_profile, default_events_register_stream_name)

    bot_profile = do_create_user(email=email, password='',
                                 realm=user_profile.realm, full_name=full_name,
                                 short_name=short_name, active=True,
                                 bot_type=bot_type,
                                 bot_owner=user_profile,
                                 avatar_source=avatar_source,
                                 default_sending_stream=default_sending_stream,
                                 default_events_register_stream=default_events_register_stream,
                                 default_all_public_streams=default_all_public_streams)
    if len(request.FILES) == 1:
        user_file = list(request.FILES.values())[0]
        upload_avatar_image(user_file, user_profile, bot_profile)

    if bot_type in (UserProfile.OUTGOING_WEBHOOK_BOT, UserProfile.EMBEDDED_BOT):
        add_service(name=service_name,
                    user_profile=bot_profile,
                    base_url=payload_url,
                    interface=interface_type,
                    token=random_api_key())

    json_result = dict(
        api_key=bot_profile.api_key,
        avatar_url=avatar_url(bot_profile),
        default_sending_stream=get_stream_name(bot_profile.default_sending_stream),
        default_events_register_stream=get_stream_name(bot_profile.default_events_register_stream),
        default_all_public_streams=bot_profile.default_all_public_streams,
    )
    return json_success(json_result)