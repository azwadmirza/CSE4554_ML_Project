    def __init__(self, channel_id, num_votes, num_torrents, swarm_size_sum, timestamp):
        super(ChannelHealthPayload, self).__init__()
        self.channel_id = channel_id
        self.num_votes = num_votes or 0
        self.num_torrents = num_torrents or 0
        self.swarm_size_sum = swarm_size_sum or 0
        self.timestamp = timestamp or -1