	def __init__(self, fileManager, analysisQueue, printerProfileManager):
		from collections import deque

		self._logger = logging.getLogger(__name__)

		self._dict = frozendict if settings().getBoolean(["devel", "useFrozenDictForPrinterState"]) else dict

		self._analysisQueue = analysisQueue
		self._fileManager = fileManager
		self._printerProfileManager = printerProfileManager

		# state
		# TODO do we really need to hold the temperature here?
		self._temp = None
		self._bedTemp = None
		self._targetTemp = None
		self._targetBedTemp = None
		self._temps = TemperatureHistory(cutoff=settings().getInt(["temperature", "cutoff"])*60)
		self._tempBacklog = []

		self._messages = deque([], 300)
		self._messageBacklog = []

		self._log = deque([], 300)
		self._logBacklog = []

		self._state = None

		self._currentZ = None

		self._printAfterSelect = False
		self._posAfterSelect = None

		# sd handling
		self._sdPrinting = False
		self._sdStreaming = False
		self._sdFilelistAvailable = threading.Event()
		self._streamingFinishedCallback = None
		self._streamingFailedCallback = None

		# job handling & estimation
		self._selectedFileMutex = threading.RLock()
		self._selectedFile = None

		self._estimator_factory = PrintTimeEstimator
		analysis_queue_hooks = plugin_manager().get_hooks("octoprint.printer.estimation.factory")
		for name, hook in analysis_queue_hooks.items():
			try:
				estimator = hook()
				if estimator is not None:
					self._logger.info("Using print time estimator provided by {}".format(name))
					self._estimator_factory = estimator
			except:
				self._logger.exception("Error while processing analysis queues from {}".format(name))

		# comm
		self._comm = None

		# callbacks
		self._callbacks = []

		# progress plugins
		self._lastProgressReport = None
		self._progressPlugins = plugin_manager().get_implementations(ProgressPlugin)

		self._stateMonitor = StateMonitor(
			interval=0.5,
			on_update=self._sendCurrentDataCallbacks,
			on_add_temperature=self._sendAddTemperatureCallbacks,
			on_add_log=self._sendAddLogCallbacks,
			on_add_message=self._sendAddMessageCallbacks,
			on_get_progress=self._updateProgressDataCallback
		)
		self._stateMonitor.reset(
			state=self._dict(text=self.get_state_string(), flags=self._getStateFlags()),
			job_data=self._dict(file=self._dict(name=None,
			                                    path=None,
			                                    size=None,
			                                    origin=None,
			                                    date=None),
			                    estimatedPrintTime=None,
			                    lastPrintTime=None,
			                    filament=self._dict(length=None,
			                                        volume=None),
			                    user=None),
			progress=self._dict(completion=None,
			                    filepos=None,
			                    printTime=None,
			                    printTimeLeft=None,
			                    printTimeOrigin=None),
			current_z=None,
			offsets=self._dict()
		)

		eventManager().subscribe(Events.METADATA_ANALYSIS_FINISHED, self._on_event_MetadataAnalysisFinished)
		eventManager().subscribe(Events.METADATA_STATISTICS_UPDATED, self._on_event_MetadataStatisticsUpdated)