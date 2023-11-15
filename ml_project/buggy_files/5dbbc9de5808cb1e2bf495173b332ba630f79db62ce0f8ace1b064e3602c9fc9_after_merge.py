	def set_compact(self, state): # TODO state as an int
		if state:
			self.main_menu_btn.set_menu_model(self.long_main_menu)
		else:
			self.main_menu_btn.set_menu_model(self.short_main_menu)
		self.save_label.set_visible(not state)
		self.save_icon.set_visible(state)
		self.hidable_widget.set_visible(not state)
		self.new_btn.set_visible(not state)
		self.is_narrow = state