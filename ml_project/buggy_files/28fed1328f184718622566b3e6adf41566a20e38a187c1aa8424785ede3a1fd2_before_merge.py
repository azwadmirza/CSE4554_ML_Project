def cli_redis_export(cmd, client, resource_group_name, name, prefix, container, file_format=None):
    from azure.mgmt.redis.models import ExportRDBParameters
    parameters = ExportRDBParameters(prefix, container, file_format)
    return client.export_data(resource_group_name, name, parameters)