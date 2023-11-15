def _get_django_admin(bin_env):
    '''
    Return the django admin
    '''
    if not bin_env:
        if salt.utils.which('django-admin.py'):
            return 'django-admin.py'
        elif salt.utils.which('django-admin'):
            return 'django-admin'
        else:
            raise salt.exceptions.CommandExecutionError(
                    "django-admin or django-admin.py not found on PATH")

    # try to get django-admin.py bin from env
    if os.path.exists(os.path.join(bin_env, 'bin', 'django-admin.py')):
        return os.path.join(bin_env, 'bin', 'django-admin.py')
    return bin_env