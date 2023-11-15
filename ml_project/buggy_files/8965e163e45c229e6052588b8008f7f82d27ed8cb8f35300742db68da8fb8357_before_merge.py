def update_subproject(request, project, subproject):
    '''
    API hook for updating git repos.
    '''
    if not settings.ENABLE_HOOKS:
        return HttpResponseNotAllowed([])
    obj = get_object_or_404(SubProject, slug=subproject, project__slug=project)
    thread = threading.Thread(target=obj.do_update)
    thread.start()
    return HttpResponse('update triggered')