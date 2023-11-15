    def attach(self, laddr: Union[str, Tuple]) -> None:
        """Attaches to an already running RPC client subprocess.

        Args:
            laddr: Address that the client is listening at. Can be supplied as a
                   string "http://127.0.0.1:8545" or tuple ("127.0.0.1", 8545)"""
        if self.is_active():
            raise SystemError("RPC is already active.")
        if isinstance(laddr, str):
            o = urlparse(laddr)
            if not o.port:
                raise ValueError("No RPC port given")
            laddr = (o.hostname, o.port)
        try:
            proc = next(i for i in psutil.process_iter() if _check_connections(i, laddr))
        except StopIteration:
            raise ProcessLookupError("Could not find RPC process.")
        print(f"Attached to local RPC client listening at '{laddr[0]}:{laddr[1]}'...")
        self._rpc = psutil.Process(proc.pid)
        if web3.provider:
            self._reset_id = self._snap()
        _notify_registry(0)