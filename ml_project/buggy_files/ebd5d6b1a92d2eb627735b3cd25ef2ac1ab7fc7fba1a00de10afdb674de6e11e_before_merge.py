def process_system_info_telemetry(telemetry_json):
    process_ssh_info(telemetry_json)
    process_credential_info(telemetry_json)
    process_mimikatz_and_wmi_info(telemetry_json)
    process_aws_data(telemetry_json)
    update_db_with_new_hostname(telemetry_json)
    test_antivirus_existence(telemetry_json)