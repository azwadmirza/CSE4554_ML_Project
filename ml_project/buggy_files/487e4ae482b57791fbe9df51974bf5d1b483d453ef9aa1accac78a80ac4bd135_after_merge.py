def deployment_validate_table_format(result):

    if result.get('error', None):
        error_result = OrderedDict()
        error_result['result'] = result['error']['code']
        try:
            tracking_id = re.match(r".*(\w{8}-\w{4}-\w{4}-\w{4}-\w{12})", str(result['error']['message'])).group(1)
            error_result['trackingId'] = tracking_id
        except:  # pylint: disable=bare-except
            pass
        try:
            error_result['message'] = result['error']['details'][0]['message']
        except:  # pylint: disable=bare-except
            error_result['message'] = result['error']['message']
        return error_result
    elif result.get('properties', None):
        success_result = OrderedDict()
        success_result['result'] = result['properties']['provisioningState']
        success_result['correlationId'] = result['properties']['correlationId']
        return success_result
    return result