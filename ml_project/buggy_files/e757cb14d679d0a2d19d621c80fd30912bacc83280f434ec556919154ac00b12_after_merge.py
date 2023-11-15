def volume_present(name, driver=None, driver_opts=None, force=False):
    '''
    Ensure that a volume is present.

    .. versionadded:: 2015.8.4

    .. versionchanged:: 2015.8.6
        This function no longer deletes and re-creates a volume if the
        existing volume's driver does not match the ``driver``
        parameter (unless the ``force`` parameter is set to ``True``).

    name
        Name of the volume

    driver
        Type of driver for that volume.  If ``None`` and the volume
        does not yet exist, the volume will be created using Docker's
        default driver.  If ``None`` and the volume does exist, this
        function does nothing, even if the existing volume's driver is
        not the Docker default driver.  (To ensure that an existing
        volume's driver matches the Docker default, you must
        explicitly name Docker's default driver here.)

    driver_opts
        Options for the volume driver

    force : False
        If the volume already exists but the existing volume's driver
        does not match the driver specified by the ``driver``
        parameter, this parameter controls whether the function errors
        out (if ``False``) or deletes and re-creates the volume (if
        ``True``).

        .. versionadded:: 2015.8.6

    Usage Examples:

    .. code-block:: yaml

        volume_foo:
          dockerng.volume_present


    .. code-block:: yaml

        volume_bar:
          dockerng.volume_present
            - name: bar
            - driver: local
            - driver_opts:
                foo: bar

    .. code-block:: yaml

        volume_bar:
          dockerng.volume_present
            - name: bar
            - driver: local
            - driver_opts:
                - foo: bar
                - option: value

    '''
    ret = {'name': name,
           'changes': {},
           'result': False,
           'comment': ''}
    if salt.utils.is_dictlist(driver_opts):
        driver_opts = salt.utils.repack_dictlist(driver_opts)
    volume = _find_volume(name)
    if not volume:
        try:
            ret['changes']['created'] = __salt__['dockerng.create_volume'](
                name, driver=driver, driver_opts=driver_opts)
        except Exception as exc:
            ret['comment'] = ('Failed to create volume \'{0}\': {1}'
                              .format(name, exc))
            return ret
        else:
            result = True
            ret['result'] = result
            return ret
    # volume exits, check if driver is the same.
    if driver is not None and volume['Driver'] != driver:
        if not force:
            ret['comment'] = "Driver for existing volume '{0}' ('{1}')" \
                             " does not match specified driver ('{2}')" \
                             " and force is False".format(
                                 name, volume['Driver'], driver)
            return ret
        try:
            ret['changes']['removed'] = __salt__['dockerng.remove_volume'](name)
        except Exception as exc:
            ret['comment'] = ('Failed to remove volume \'{0}\': {1}'
                              .format(name, exc))
            return ret
        else:
            try:
                ret['changes']['created'] = __salt__['dockerng.create_volume'](
                    name, driver=driver, driver_opts=driver_opts)
            except Exception as exc:
                ret['comment'] = ('Failed to create volume \'{0}\': {1}'
                                .format(name, exc))
                return ret
            else:
                result = True
                ret['result'] = result
                return ret

    ret['result'] = True
    ret['comment'] = 'Volume \'{0}\' already exists.'.format(name)
    return ret