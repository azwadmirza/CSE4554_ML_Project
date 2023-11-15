def login_page(request, **kwargs):
    # type: (HttpRequest, **Any) -> HttpResponse
    if request.user.is_authenticated:
        return HttpResponseRedirect(request.user.realm.uri)
    if is_subdomain_root_or_alias(request) and settings.ROOT_DOMAIN_LANDING_PAGE:
        redirect_url = reverse('zerver.views.registration.find_account')
        return HttpResponseRedirect(redirect_url)

    realm = get_realm_from_request(request)
    if realm and realm.deactivated:
        return redirect_to_deactivation_notice()

    extra_context = kwargs.pop('extra_context', {})
    if dev_auth_enabled():
        if 'new_realm' in request.POST:
            realm = get_realm(request.POST['new_realm'])
        else:
            realm = get_realm_from_request(request)

        users = get_dev_users(realm)
        extra_context['current_realm'] = realm
        extra_context['all_realms'] = Realm.objects.all()

        extra_context['direct_admins'] = [u for u in users if u.is_realm_admin]
        extra_context['direct_users'] = [u for u in users if not u.is_realm_admin]

        if 'new_realm' in request.POST:
            # If we're switching realms, redirect to that realm
            return HttpResponseRedirect(realm.uri)

    try:
        template_response = django_login_page(
            request, authentication_form=OurAuthenticationForm,
            extra_context=extra_context, **kwargs)
    except ZulipLDAPConfigurationError as e:
        assert len(e.args) > 1
        return redirect_to_misconfigured_ldap_notice(e.args[1])

    try:
        template_response.context_data['email'] = request.GET['email']
    except KeyError:
        pass

    try:
        already_registered = request.GET['already_registered']
        template_response.context_data['already_registered'] = already_registered
    except KeyError:
        pass

    try:
        template_response.context_data['subdomain'] = request.GET['subdomain']
        template_response.context_data['wrong_subdomain_error'] = WRONG_SUBDOMAIN_ERROR
    except KeyError:
        pass

    return template_response