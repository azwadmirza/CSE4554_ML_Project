def configure(config):
    config.define_section('meetbot', MeetbotSection)
    config.meetbot.configure_setting('meeting_log_path')
    config.meetbot.configure_setting('meeting_log_baseurl')