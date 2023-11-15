def update_db_with_new_hostname(telemetry_json):
    Monkey.get_single_monkey_by_id(telemetry_json['_id']).set_hostname(telemetry_json['data']['hostname'])