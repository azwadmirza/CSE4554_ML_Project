def image_present(name,
                  build=None,
                  load=None,
                  force=False,
                  insecure_registry=False,
                  client_timeout=CLIENT_TIMEOUT):
    '''
    Ensure that an image is present. The image can either be pulled from a
    Docker registry, built from a Dockerfile, or loaded from a saved image.
    Image names can be specified either using ``repo:tag`` notation, or just
    the repo name (in which case a tag of ``latest`` is assumed).

    If neither of the ``build`` or ``load`` arguments are used, then Salt will
    pull from the :ref:`configured registries <docker-authentication>`. If the
    specified image already exists, it will not be pulled unless ``force`` is
    set to ``True``. Here is an example of a state that will pull an image from
    the Docker Hub:

    .. code-block:: yaml

        myuser/myimage:mytag:
          dockerng.image_present

    build
        Path to directory on the Minion containing a Dockerfile

        .. code-block:: yaml

            myuser/myimage:mytag:
              dockerng.image_present:
                - build: /home/myuser/docker/myimage

        The image will be built using :py:func:`dockerng.build
        <salt.modules.dockerng.build>` and the specified image name and tag
        will be applied to it.

    load
        Loads a tar archive created with :py:func:`dockerng.load
        <salt.modules.dockerng.load>` (or the ``docker load`` Docker CLI
        command), and assigns it the specified repo and tag.

        .. code-block:: yaml

            myuser/myimage:mytag:
              dockerng.image_present:
                - load: salt://path/to/image.tar

    force : False
        Set this parameter to ``True`` to force Salt to pull/build/load the
        image even if it is already present.

    client_timeout
        Timeout in seconds for the Docker client. This is not a timeout for
        the state, but for receiving a response from the API.
    '''
    ret = {'name': name,
           'changes': {},
           'result': False,
           'comment': ''}

    if build is not None and load is not None:
        ret['comment'] = 'Only one of \'build\' or \'load\' is permitted.'
        return ret

    # Ensure that we have repo:tag notation
    image = ':'.join(_get_repo_tag(name))
    all_tags = __salt__['dockerng.list_tags']()

    if image in all_tags:
        if not force:
            ret['result'] = True
            ret['comment'] = 'Image \'{0}\' already present'.format(name)
            return ret
        else:
            try:
                image_info = __salt__['dockerng.inspect_image'](name)
            except Exception as exc:
                ret['comment'] = \
                    'Unable to get info for image \'{0}\': {1}'.format(name, exc)
                return ret
    else:
        image_info = None

    if build:
        action = 'built'
    elif load:
        action = 'loaded'
    else:
        action = 'pulled'

    if __opts__['test']:
        ret['result'] = None
        if (image in all_tags and force) or image not in all_tags:
            ret['comment'] = 'Image \'{0}\' will be {1}'.format(name, action)
            return ret

    if build:
        try:
            image_update = __salt__['dockerng.build'](path=build, image=image)
        except Exception as exc:
            ret['comment'] = (
                'Encountered error building {0} as {1}: {2}'
                .format(build, image, exc)
            )
            return ret
        if image_info is None or image_update['Id'] != image_info['Id'][:12]:
            ret['changes'] = image_update

    elif load:
        try:
            image_update = __salt__['dockerng.load'](path=load, image=image)
        except Exception as exc:
            ret['comment'] = (
                'Encountered error loading {0} as {1}: {2}'
                .format(load, image, exc)
            )
            return ret
        if image_info is None or image_update.get('Layers', []):
            ret['changes'] = image_update

    else:
        try:
            image_update = __salt__['dockerng.pull'](
                image,
                insecure_registry=insecure_registry,
                client_timeout=client_timeout
            )
        except Exception as exc:
            ret['comment'] = (
                'Encountered error pulling {0}: {1}'
                .format(image, exc)
            )
            return ret
        if (image_info is not None and image_info['Id'][:12] == image_update
                .get('Layers', {})
                .get('Already_Pulled', [None])[0]):
            # Image was pulled again (because of force) but was also
            # already there. No new image was available on the registry.
            pass
        elif image_info is None or image_update.get('Layers', {}).get('Pulled'):
            # Only add to the changes dict if layers were pulled
            ret['changes'] = image_update

    ret['result'] = image in __salt__['dockerng.list_tags']()

    if not ret['result']:
        # This shouldn't happen, failure to pull should be caught above
        ret['comment'] = 'Image \'{0}\' could not be {1}'.format(name, action)
    elif not ret['changes']:
        ret['comment'] = (
            'Image \'{0}\' was {1}, but there were no changes'
            .format(name, action)
        )
    else:
        ret['comment'] = 'Image \'{0}\' was {1}'.format(name, action)
    return ret