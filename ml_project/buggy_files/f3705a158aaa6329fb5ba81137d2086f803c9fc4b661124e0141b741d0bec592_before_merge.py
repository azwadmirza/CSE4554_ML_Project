def build(path=None,
          image=None,
          cache=True,
          rm=True,
          api_response=False,
          fileobj=None):
    '''
    Builds a docker image from a Dockerfile or a URL

    path
        Path to directory on the Minion containing a Dockerfile

    image
        Image to be built, in ``repo:tag`` notation. If just the repository
        name is passed, a tag name of ``latest`` will be assumed. If building
        from a URL, this parameted can be omitted.

    cache : True
        Set to ``False`` to force the build process not to use the Docker image
        cache, and pull all required intermediate image layers

    rm : True
        Remove intermediate containers created during build

    api_response : False
        If ``True``: an ``API_Response`` key will be present in the return
        data, containing the raw output from the Docker API.

    fileobj
        Allows for a file-like object containing the contents of the Dockerfile
        to be passed in place of a file ``path`` argument. This argument should
        not be used from the CLI, only from other Salt code.


    **RETURN DATA**

    A dictionary containing one or more of the following keys:

    - ``Id`` - ID of the newly-built image
    - ``Time_Elapsed`` - Time in seconds taken to perform the build
    - ``Intermediate_Containers`` - IDs of containers created during the course
      of the build process

      *(Only present if rm=False)*
    - ``Images`` - A dictionary containing one or more of the following keys:
        - ``Already_Pulled`` - Layers that that were already present on the
          Minion
        - ``Pulled`` - Layers that that were pulled

      *(Only present if the image specified by the "image" argument was not
      present on the Minion, or if cache=False)*
    - ``Status`` - A string containing a summary of the pull action (usually a
      message saying that an image was downloaded, or that it was up to date).

      *(Only present if the image specified by the "image" argument was not
      present on the Minion, or if cache=False)*


    CLI Example:

    .. code-block:: bash

        salt myminion dockerng.build /path/to/docker/build/dir image=myimage:dev
        salt myminion dockerng.build https://github.com/myuser/myrepo.git image=myimage:latest
    '''
    _prep_pull()

    image = ':'.join(_get_repo_tag(image))
    time_started = time.time()
    response = _client_wrapper('build',
                               path=path,
                               tag=image,
                               quiet=False,
                               fileobj=fileobj,
                               rm=rm,
                               nocache=not cache)
    ret = {'Time_Elapsed': time.time() - time_started}
    _clear_context()

    if not response:
        raise CommandExecutionError(
            'Build failed for {0}, no response returned from Docker API'
            .format(image)
        )

    stream_data = [json.loads(x) for x in response]
    errors = []
    # Iterate through API response and collect information
    for item in stream_data:
        try:
            item_type = next(iter(item))
        except StopIteration:
            continue
        if item_type == 'status':
            _pull_status(ret, item)
        if item_type == 'stream':
            _build_status(ret, item)
        elif item_type == 'errorDetail':
            _error_detail(errors, item)

    if 'Id' not in ret:
        # API returned information, but there was no confirmation of a
        # successful build.
        msg = 'Build failed for {0}'.format(image)
        log.error(msg)
        log.error(stream_data)
        if errors:
            msg += '. Error(s) follow:\n\n{0}'.format(
                '\n\n'.join(errors)
            )
        raise CommandExecutionError(msg)

    for image_id, image_info in six.iteritems(images()):
        if image_id.startswith(ret['Id']):
            if image in image_info.get('RepoTags', []):
                ret['Image'] = image
            else:
                ret['Warning'] = \
                    'Failed to tag image as {0}'.format(image)

    if api_response:
        ret['API_Response'] = stream_data

    if rm:
        ret.pop('Intermediate_Containers', None)
    return ret