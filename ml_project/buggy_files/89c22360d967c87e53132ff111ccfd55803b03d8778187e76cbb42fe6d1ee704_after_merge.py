def configure(config):
    config.define_section('meetbot', MeetbotSection)
    config.meetbot.configure_setting(
        'meeting_log_path',
        'Enter the directory to store logs in.'
    )
    config.meetbot.configure_setting(
        'meeting_log_baseurl',
        'Enter the base URL for the meeting logs.',
    )