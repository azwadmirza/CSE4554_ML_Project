    def __init__(self, cookie_dir):
        self.do_not_track = True
        self.cookie_dir = cookie_dir

        self.id = None
        self.invocation_id = str(uuid.uuid4())
        self.run_started_at = datetime.now(tz=pytz.utc)