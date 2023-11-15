def update_project(request, project):
    '''
    API hook for updating git repos.
    '''
    if not appsettings.ENABLE_HOOKS:
        return HttpResponseNotAllowed([])
    obj = get_object_or_404(Project, slug=project)
    thread = threading.Thread(target=obj.do_update)
    thread.start()
    return HttpResponse('update triggered')