	def on_created(self, event):
		thread = threading.Thread(target=self._repeatedly_check, args=(event.src_path,))
		thread.daemon = True
		thread.start()