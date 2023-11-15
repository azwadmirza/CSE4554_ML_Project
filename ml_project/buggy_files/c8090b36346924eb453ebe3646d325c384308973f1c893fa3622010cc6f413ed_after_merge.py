	def _set_active_type(self, *args):
		state_as_string = self.get_option_value('filters_type')
		self._reset_type_values()
		if state_as_string == 'blur_fast':
			self.blur_algo = BlurType.CAIRO_REPAINTS
			self.type_label =  _("Fast blur")
		elif state_as_string == 'blur_slow':
			self.blur_algo = BlurType.PX_BOX
			self.type_label = _("Slow blur")
		elif state_as_string == 'tiles':
			self.blur_algo = BlurType.TILES
			self.type_label = _("Pixelization")
		elif state_as_string == 'saturation':
			self.saturate = True
			self.type_label = _("Change saturation")
		elif state_as_string == 'veil':
			self.pixelate = True
			self.type_label = _("Veil")
		elif state_as_string == 'invert':
			self.invert = True
			self.type_label = _("Invert colors")
		elif state_as_string == 'transparency':
			self.transparency = True
			self.type_label = _("Add transparency")
		else:
			self.type_label = _("Select a filter…")
		self.bar.on_filter_changed()