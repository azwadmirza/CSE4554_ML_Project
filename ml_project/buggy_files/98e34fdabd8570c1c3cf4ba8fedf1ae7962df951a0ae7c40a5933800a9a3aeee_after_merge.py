def save_user_session_membership(sender, **kwargs):
    session = kwargs.get('instance', None)
    if pkg_resources.get_distribution('channels').version >= '2':
        # If you get into this code block, it means we upgraded channels, but
        # didn't make the settings.SESSIONS_PER_USER feature work
        raise RuntimeError(
            'save_user_session_membership must be updated for channels>=2: '
            'http://channels.readthedocs.io/en/latest/one-to-two.html#requirements'
        )
    if 'runworker' in sys.argv:
        # don't track user session membership for websocket per-channel sessions
        return
    if not session:
        return
    user_id = session.get_decoded().get(SESSION_KEY, None)
    if not user_id:
        return
    if UserSessionMembership.objects.filter(user=user_id, session=session).exists():
        return
    # check if user_id from session has an id match in User before saving
    if User.objects.filter(id=int(user_id)).exists():
        UserSessionMembership(user_id=user_id, session=session, created=timezone.now()).save()
        expired = UserSessionMembership.get_memberships_over_limit(user_id)
        for membership in expired:
            Session.objects.filter(session_key__in=[membership.session_id]).delete()
            membership.delete()
        if len(expired):
            consumers.emit_channel_notification(
                'control-limit_reached_{}'.format(user_id),
                dict(group_name='control', reason='limit_reached')
            )