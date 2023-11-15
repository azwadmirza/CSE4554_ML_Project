def configure(config):
    config.define_section('safety', SafetySection)
    config.safety.configure_setting('enabled_by_default')
    config.safety.configure_setting('known_good')
    config.safety.configure_setting(
        'vt_api_key',
        "Optionaly, enter a VirusTotal API key to improve malicious URL "
        "protection. Otherwise, only the Malwarebytes DB will be used."
    )