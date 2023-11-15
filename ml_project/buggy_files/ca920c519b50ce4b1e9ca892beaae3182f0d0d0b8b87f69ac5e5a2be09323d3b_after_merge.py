def get_provider_pool():
    """Return the subliminal provider pool to be used.

    :return: subliminal provider pool to be used
    :rtype: subliminal.ProviderPool
    """
    logger.debug(u'Creating a new ProviderPool instance')
    provider_configs = {'addic7ed': {'username': sickbeard.ADDIC7ED_USER,
                                     'password': sickbeard.ADDIC7ED_PASS},
                        'itasa': {'username': sickbeard.ITASA_USER,
                                  'password': sickbeard.ITASA_PASS},
                        'legendastv': {'username': sickbeard.LEGENDASTV_USER,
                                       'password': sickbeard.LEGENDASTV_PASS},
                        'opensubtitles': {'username': sickbeard.OPENSUBTITLES_USER,
                                          'password': sickbeard.OPENSUBTITLES_PASS}}
    return ProviderPool(providers=enabled_service_list(), provider_configs=provider_configs)