def install_ruby(ruby, runas=None):
    '''
    Install a ruby implementation.

    ruby
        The version of Ruby to install, should match one of the
        versions listed by :py:func:`rbenv.list <salt.modules.rbenv.list>`

    runas
        The user under which to run rbenv. If not specified, then rbenv will be
        run as the user under which Salt is running.

    Additional environment variables can be configured in pillar /
    grains / master:

    .. code-block:: yaml

        rbenv:
          build_env: 'CONFIGURE_OPTS="--no-tcmalloc" CFLAGS="-fno-tree-dce"'

    CLI Example:

    .. code-block:: bash

        salt '*' rbenv.install_ruby 2.0.0-p0
    '''
    ruby = re.sub(r'^ruby-', '', ruby)

    env = None
    env_list = []

    if __grains__['os'] in ('FreeBSD', 'NetBSD', 'OpenBSD'):
        env_list.append('MAKE=gmake')

    if __salt__['config.get']('rbenv:build_env'):
        env_list.append(__salt__['config.get']('rbenv:build_env'))
    elif __salt__['config.option']('rbenv.build_env'):
        env_list.append(__salt__['config.option']('rbenv.build_env'))

    if env_list:
        env = ' '.join(env_list)

    ret = {}
    ret = _rbenv_exec(['install', ruby], env=env, runas=runas, ret=ret)
    if ret['retcode'] == 0:
        rehash(runas=runas)
        return ret['stderr']
    else:
        # Cleanup the failed installation so it doesn't list as installed
        uninstall_ruby(ruby, runas=runas)
        return False