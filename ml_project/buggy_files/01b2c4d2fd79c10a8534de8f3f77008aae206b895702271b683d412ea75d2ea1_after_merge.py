    def __init__(self, packet_manager: packet.PacketManager) -> None:
        self.packet_manager = packet_manager
        self.current_judge_worker: Optional[JudgeWorker] = None
        # Locks current_judge_worker assignments. RLock so that self.current_submission can be used while already
        # behing held.
        self._current_submission_lock = threading.RLock()
        self._grading_lock = threading.Lock()

        self.updater_exit = False
        self.updater_signal = threading.Event()
        self.updater = threading.Thread(target=self._updater_thread)