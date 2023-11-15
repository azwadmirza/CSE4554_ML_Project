    def __init__(self, loop: asyncio.AbstractEventLoop, config: 'Config', blob_manager: 'BlobManager',
                 wallet_manager: 'WalletManager', storage: 'SQLiteStorage', node: Optional['Node'],
                 analytics_manager: Optional['AnalyticsManager'] = None):
        self.loop = loop
        self.config = config
        self.blob_manager = blob_manager
        self.wallet_manager = wallet_manager
        self.storage = storage
        self.node = node
        self.analytics_manager = analytics_manager
        self.streams: typing.Dict[str, ManagedStream] = {}
        self.resume_saving_task: Optional[asyncio.Task] = None
        self.re_reflect_task: Optional[asyncio.Task] = None
        self.update_stream_finished_futs: typing.List[asyncio.Future] = []
        self.running_reflector_uploads: typing.Dict[str, asyncio.Task] = {}
        self.started = asyncio.Event(loop=self.loop)