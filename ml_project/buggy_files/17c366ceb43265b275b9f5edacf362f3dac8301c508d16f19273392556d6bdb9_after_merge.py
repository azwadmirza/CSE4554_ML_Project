def get_project(conn, vm_):
    '''
    Return the project to use.
    '''
    try:
        projects = conn.ex_list_projects()
    except AttributeError:
        # with versions <0.15 of libcloud this is causing an AttributeError.
        return False
    projid = config.get_cloud_config_value('projectid', vm_, __opts__)

    if not projid:
        return False

    for project in projects:
        if str(projid) in (str(project.id), str(project.name)):
            return project

    log.warning("Couldn't find project {0} in projects".format(projid))
    return False