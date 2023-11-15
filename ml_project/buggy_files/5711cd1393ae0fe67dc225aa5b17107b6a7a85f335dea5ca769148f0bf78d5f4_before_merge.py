def configure(config):
    """
    | name | example | purpose |
    | ---- | ------- | ------- |
    | enabled\\_by\\_default | True | Enable URL safety in all channels where it isn't explicitly disabled. |
    | known\\_good | sopel.chat,dftba.net | List of "known good" domains to ignore. |
    | vt\\_api\\_key | 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef | Optional VirusTotal API key to improve malicious URL detection |
    """
    config.define_section('safety', SafetySection)
    config.safety.configure_setting(
        'enabled_by_default',
        "Enable URL safety in channels that don't specifically disable it?",
    )
    config.safety.configure_setting(
        'known_good',
        'Enter any domains to whitelist',
    )
    config.safety.configure_setting(
        'vt_api_key',
        "Optionally, enter a VirusTotal API key to improve malicious URL "
        "protection.\nOtherwise, only the Malwarebytes DB will be used."
    )