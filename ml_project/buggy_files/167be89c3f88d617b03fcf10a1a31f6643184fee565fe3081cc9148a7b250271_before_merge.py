def _get_django_admin(bin_env):
    '''
    Return the django admin
    '''
    if not bin_env:
        return 'django-admin.py'

    # try to get django-admin.py bin from env
    if os.path.exists(os.path.join(bin_env, 'bin', 'django-admin.py')):
        return os.path.join(bin_env, 'bin', 'django-admin.py')
    return bin_env