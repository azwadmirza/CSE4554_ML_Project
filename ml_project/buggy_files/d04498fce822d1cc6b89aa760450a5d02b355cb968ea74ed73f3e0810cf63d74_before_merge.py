def _get_app_object_id_from_sp_object_id(client, sp_object_id):
    sp = client.service_principals.get(sp_object_id)
    app_object_id = None

    if sp.service_principal_names:
        result = list(client.applications.list(
            filter="identifierUris/any(s:s eq '{}')".format(sp.service_principal_names[0])))
        if result:
            app_object_id = result[0].object_id
    return app_object_id