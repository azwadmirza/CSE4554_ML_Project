def _get_ttl():
    return __opts__.get('keep_jobs', 24) * 3600