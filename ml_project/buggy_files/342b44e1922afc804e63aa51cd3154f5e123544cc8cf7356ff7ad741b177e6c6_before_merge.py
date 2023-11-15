    def __init__(self):
        self.do_not_track = True

        self.id = None
        self.invocation_id = str(uuid.uuid4())
        self.run_started_at = datetime.now(tz=pytz.utc)