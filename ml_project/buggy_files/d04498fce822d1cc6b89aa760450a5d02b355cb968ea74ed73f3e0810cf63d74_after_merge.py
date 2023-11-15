def _get_app_object_id_from_sp_object_id(client, sp_object_id):
    sp = client.service_principals.get(sp_object_id)
    result = list(client.applications.list(filter="appId eq '{}'".format(sp.app_id)))

    if result:
        return result[0].object_id
    raise CLIError("Can't find associated application id from '{}'".format(sp_object_id))