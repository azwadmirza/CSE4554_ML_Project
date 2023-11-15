def performance(request):
    '''
    Shows performance tuning tips.
    '''
    checks = []
    # Check for debug mode
    checks.append((
        _('Debug mode'),
        not settings.DEBUG,
        'production-debug',
    ))
    # Check for domain configuration
    checks.append((
        _('Site domain'),
        Site.objects.get_current() != 'example.net',
        'production-site',
    ))
    # Check database being used
    checks.append((
        _('Database backend'),
        "sqlite" not in settings.DATABASES['default']['ENGINE'],
        'production-database',
    ))
    # Check configured admins
    checks.append((
        _('Site administrator'),
        len(settings.ADMINS) > 0,
        'production-admins',
    ))
    # Check offloading indexing
    checks.append((
        # Translators: Indexing is postponed to cron job
        _('Indexing offloading'),
        settings.OFFLOAD_INDEXING,
        'production-indexing',
    ))
    # Check for sane caching
    cache = settings.CACHES['default']['BACKEND'].split('.')[-1]
    if cache in ['MemcachedCache', 'DatabaseCache']:
        # We consider these good
        cache = True
    elif cache in ['DummyCache']:
        # This one is definitely bad
        cache = False
    else:
        # These might not be that bad
        cache = None
    checks.append((
        _('Django caching'),
        cache,
        'production-cache',
    ))
    # Check email setup
    default_mails = (
        'root@localhost',
        'webmaster@localhost',
        'noreply@weblate.org'
    )
    checks.append((
        _('Email addresses'),
        (
            settings.SERVER_EMAIL not in default_mails
            and settings.DEFAULT_FROM_EMAIL not in default_mails
        ),
        'production-email',
    ))
    return render_to_response(
        "admin/performance.html",
        RequestContext(
            request,
            {
                'checks': checks,
            }
        )
    )