	def _updateProgressDataCallback(self):
		if self._comm is None:
			progress = None
			filepos = None
			printTime = None
			cleanedPrintTime = None
		else:
			progress = self._comm.getPrintProgress()
			filepos = self._comm.getPrintFilepos()
			printTime = self._comm.getPrintTime()
			cleanedPrintTime = self._comm.getCleanedPrintTime()

		printTimeLeft = printTimeLeftOrigin = None
		estimator = self._estimator
		if progress is not None:
			progress_int = int(progress * 100)
			if self._lastProgressReport != progress_int:
				self._lastProgressReport = progress_int
				self._reportPrintProgressToPlugins(progress_int)

			if progress == 0:
				printTimeLeft = None
				printTimeLeftOrigin = None
			elif progress == 1.0:
				printTimeLeft = 0
				printTimeLeftOrigin = None
			elif estimator is not None:
				statisticalTotalPrintTime = None
				statisticalTotalPrintTimeType = None
				with self._selectedFileMutex:
					if self._selectedFile and "estimatedPrintTime" in self._selectedFile \
							and self._selectedFile["estimatedPrintTime"]:
						statisticalTotalPrintTime = self._selectedFile["estimatedPrintTime"]
						statisticalTotalPrintTimeType = self._selectedFile.get("estimatedPrintTimeType", None)

				printTimeLeft, printTimeLeftOrigin = estimator.estimate(progress,
				                                                        printTime,
				                                                        cleanedPrintTime,
				                                                        statisticalTotalPrintTime,
				                                                        statisticalTotalPrintTimeType)

		return self._dict(completion=progress * 100 if progress is not None else None,
		                  filepos=filepos,
		                  printTime=int(printTime) if printTime is not None else None,
		                  printTimeLeft=int(printTimeLeft) if printTimeLeft is not None else None,
		                  printTimeLeftOrigin=printTimeLeftOrigin)