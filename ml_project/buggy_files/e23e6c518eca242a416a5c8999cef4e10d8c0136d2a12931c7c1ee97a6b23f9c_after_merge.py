    def __init__(self, packet_manager: packet.PacketManager) -> None:
        self.packet_manager = packet_manager
        # FIXME(tbrindus): marked as Any since PacketManager likes querying current_submission.id directly.
        self.current_submission: Any = None
        self.current_judge_worker: Optional[JudgeWorker] = None
        self._grading_lock = threading.Lock()

        self.updater_exit = False
        self.updater_signal = threading.Event()
        self.updater = threading.Thread(target=self._updater_thread)