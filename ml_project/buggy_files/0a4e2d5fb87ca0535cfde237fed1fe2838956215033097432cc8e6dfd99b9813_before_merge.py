        def _wrapped_func_arguments(request, api_key=REQ(),
                                    *args, **kwargs):
            # type: (HttpRequest, Text, *Any, **Any) -> HttpResponse
            try:
                user_profile = UserProfile.objects.get(api_key=api_key)
            except UserProfile.DoesNotExist:
                raise JsonableError(_("Invalid API key"))
            if not user_profile.is_active:
                raise JsonableError(_("Account not active"))
            if user_profile.realm.deactivated:
                raise JsonableError(_("Realm for account has been deactivated"))
            if not check_subdomain(get_subdomain(request), user_profile.realm.subdomain):
                logging.warning("User %s attempted to access webhook API on wrong subdomain %s" % (
                    user_profile.email, get_subdomain(request)))
                raise JsonableError(_("Account is not associated with this subdomain"))

            request.user = user_profile
            request._email = user_profile.email
            webhook_client_name = "Zulip{}Webhook".format(client_name)
            process_client(request, user_profile, client_name=webhook_client_name)
            if settings.RATE_LIMITING:
                rate_limit_user(request, user_profile, domain='all')
            return view_func(request, user_profile, *args, **kwargs)