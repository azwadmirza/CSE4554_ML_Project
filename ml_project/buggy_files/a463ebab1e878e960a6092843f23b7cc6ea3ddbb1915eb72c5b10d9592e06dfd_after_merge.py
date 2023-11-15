	def set_tools_labels_visibility(self, visible):
		"""Change the way tools are displayed in the side panel. Visible labels
		mean the tools will be arranged in a scrollable list of buttons, else
		they will be in an adaptative flowbox."""
		for tool_id in self.tools:
			self.tools[tool_id].label_widget.set_visible(visible)
		nb_tools = len(self.tools)
		if visible:
			self.tools_panel.set_min_children_per_line(nb_tools)
			self.tools_nonscrollable_box.remove(self.tools_panel)
			self.tools_scrollable_box.add(self.tools_panel)
		else:
			self.tools_scrollable_box.remove(self.tools_panel)
			self.tools_nonscrollable_box.add(self.tools_panel)
			nb_min = int( (nb_tools+(nb_tools % 3))/3 ) - 1
			self.tools_panel.set_min_children_per_line(nb_min)
		self.tools_panel.set_max_children_per_line(nb_tools)