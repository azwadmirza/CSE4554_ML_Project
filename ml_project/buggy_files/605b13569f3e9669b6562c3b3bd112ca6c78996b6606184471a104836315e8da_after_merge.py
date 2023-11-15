    def __init__(self, config: SimpleConfig):
        ThreadJob.__init__(self)
        # Keyed by xpub.  The value is the device id
        # has been paired, and None otherwise. Needs self.lock.
        self.xpub_ids = {}  # type: Dict[str, str]
        # A list of clients.  The key is the client, the value is
        # a (path, id_) pair. Needs self.lock.
        self.clients = {}  # type: Dict[HardwareClientBase, Tuple[Union[str, bytes], str]]
        # What we recognise.  (vendor_id, product_id) -> Plugin
        self._recognised_hardware = {}  # type: Dict[Tuple[int, int], HW_PluginBase]
        # Custom enumerate functions for devices we don't know about.
        self._enumerate_func = set()  # Needs self.lock.

        self.lock = threading.RLock()

        self.config = config