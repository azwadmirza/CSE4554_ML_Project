def github_hook(request):
    '''
    API to handle commit hooks from Github.
    '''
    if not appsettings.ENABLE_HOOKS:
        return HttpResponseNotAllowed([])
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        data = json.loads(request.POST['payload'])
    except (ValueError, KeyError):
        return HttpResponseBadRequest('could not parse json!')
    try:
        repo = 'git://github.com/%s/%s.git' % (
            data['repository']['owner']['name'],
            data['repository']['name'],
        )
        branch = data['ref'].split('/')[-1]
    except KeyError:
        return HttpResponseBadRequest('could not parse json!')
    logger.info(
        'received GitHub notification on repository %s, branch %s',
        repo,
        branch
    )
    for obj in SubProject.objects.filter(repo=repo, branch=branch):
        logger.info('GitHub notification will update %s', obj)
        thread = threading.Thread(target=obj.do_update)
        thread.start()

    return HttpResponse('update triggered')