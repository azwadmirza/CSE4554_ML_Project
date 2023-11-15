    def __init__(self,
                 data=None,
                 name=None,
                 identified_by=None,
                 id_type=None,
                 id=None,
                 episodes=1,
                 season_pack=False,
                 strict_name=False,
                 quality=None,
                 proper_count=0,
                 special=False,
                 group=None,
                 valid=True
                 ):
        self.name = name
        self.data = data
        self.episodes = episodes
        self.season_pack = season_pack
        self.identified_by = identified_by
        self.id = id
        self.id_type = id_type
        self.quality = quality if quality is not None else Quality()
        self.proper_count = proper_count
        self.special = special
        self.group = group
        self.valid = valid
        self.strict_name = strict_name