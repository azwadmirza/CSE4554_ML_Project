def update_db_with_new_hostname(telemetry_json):
    Monkey.get_single_monkey_by_guid(telemetry_json['monkey_guid']).set_hostname(telemetry_json['data']['hostname'])