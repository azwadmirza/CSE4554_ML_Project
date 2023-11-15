def share_project(request, userdb, response):
    set_default_headers(response)
    return json.dumps(userdb.create_view(get_user(request, userdb, response), request.forms.get('name'), request.forms.get('project'), request.forms.get('public')))