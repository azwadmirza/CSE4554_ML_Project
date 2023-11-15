def do_create_user(email, password, realm, full_name, short_name,
                   is_realm_admin=False, bot_type=None, bot_owner=None, tos_version=None,
                   timezone=u"", avatar_source=UserProfile.AVATAR_FROM_GRAVATAR,
                   default_sending_stream=None, default_events_register_stream=None,
                   default_all_public_streams=None, prereg_user=None,
                   newsletter_data=None, default_stream_groups=[]):
    # type: (Text, Optional[Text], Realm, Text, Text, bool, Optional[int], Optional[UserProfile], Optional[Text], Text, Text, Optional[Stream], Optional[Stream], bool, Optional[PreregistrationUser], Optional[Dict[str, str]], List[DefaultStreamGroup]) -> UserProfile

    user_profile = create_user(email=email, password=password, realm=realm,
                               full_name=full_name, short_name=short_name,
                               is_realm_admin=is_realm_admin,
                               bot_type=bot_type, bot_owner=bot_owner,
                               tos_version=tos_version, timezone=timezone, avatar_source=avatar_source,
                               default_sending_stream=default_sending_stream,
                               default_events_register_stream=default_events_register_stream,
                               default_all_public_streams=default_all_public_streams)

    event_time = user_profile.date_joined
    RealmAuditLog.objects.create(realm=user_profile.realm, modified_user=user_profile,
                                 event_type='user_created', event_time=event_time)
    do_increment_logging_stat(user_profile.realm, COUNT_STATS['active_users_log:is_bot:day'],
                              user_profile.is_bot, event_time)

    notify_created_user(user_profile)
    if bot_type:
        notify_created_bot(user_profile)
    else:
        process_new_human_user(user_profile, prereg_user=prereg_user,
                               newsletter_data=newsletter_data,
                               default_stream_groups=default_stream_groups)
    return user_profile