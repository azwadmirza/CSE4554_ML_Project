def cli_consumption_list_usage(client, billing_period_name=None, top=None, include_additional_properties=False, include_meter_details=False, start_date=None, end_date=None):
    if include_additional_properties and include_meter_details:
        expand = 'properties/additionalProperties,properties/meterDetails'
    elif include_additional_properties:
        expand = 'properties/additionalProperties'
    elif include_meter_details:
        expand = 'properties/meterDetails'
    else:
        expand = None

    filter_from = None
    filter_to = None
    filter_expression = None
    if start_date and end_date:
        filter_from = "properties/usageEnd ge \'{}\'".format(start_date.strftime("%Y-%m-%dT%H:%M:%SZ"))
        filter_to = "properties/usageEnd le \'{}\'".format(end_date.strftime("%Y-%m-%dT%H:%M:%SZ"))
        filter_expression = "{} and {}".format(filter_from, filter_to)

    if billing_period_name and top:
        return list(client.list_by_billing_period(billing_period_name, expand=expand, filter=filter_expression, top=top).advance_page())
    elif billing_period_name and not top:
        return list(client.list_by_billing_period(billing_period_name, expand=expand, filter=filter_expression))
    elif not billing_period_name and top:
        return list(client.list(expand=expand, filter=filter_expression, top=top).advance_page())
    return client.list(expand=expand, filter=filter_expression)