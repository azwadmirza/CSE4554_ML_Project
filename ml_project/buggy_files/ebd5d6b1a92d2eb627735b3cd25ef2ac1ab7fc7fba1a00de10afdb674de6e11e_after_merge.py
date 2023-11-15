def process_system_info_telemetry(telemetry_json):
    telemetry_processing_stages = [
        process_ssh_info,
        process_credential_info,
        process_mimikatz_and_wmi_info,
        process_aws_data,
        update_db_with_new_hostname,
        test_antivirus_existence,
    ]

    # Calling safe_process_telemetry so if one of the stages fail, we log and move on instead of failing the rest of
    # them, as they are independent.
    for stage in telemetry_processing_stages:
        safe_process_telemetry(stage, telemetry_json)