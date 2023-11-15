	def __init__(self, window, **kwargs):
		super().__init__('select', _("Selection"), 'tool-select-symbolic', window)
		self.use_color = False
		self.accept_selection = True

		self.selected_type_id = 'rectangle'
		self.selected_type_label = _("Rectangle selection")
		self.closing_x = 0
		self.closing_y = 0
		self.x_press = 0
		self.y_press = 0
		self.future_x = 0
		self.future_y = 0
		self.future_path = None
		self.future_pixbuf = None
		self.operation_type = None # 'op-define'
		self.behavior = 'rectangle'
		self.add_tool_action_enum('selection_type', self.selected_type_id)

		# Special bottom panel TODO common to the 3 types
		builder = Gtk.Builder.new_from_resource( \
		                '/com/github/maoschanz/drawing/tools/ui/tool_select.ui')
		self.bottom_panel = builder.get_object('bottom-panel')
		actions_menu = builder.get_object('actions-menu')
		builder.get_object('actions_btn').set_menu_model(actions_menu)
		self.import_box_narrow = builder.get_object('import_box_narrow')
		self.import_box_long = builder.get_object('import_box_long')
		self.minimap_label = builder.get_object('minimap_label')
		self.minimap_arrow = builder.get_object('minimap_arrow')
		self.minimap_icon = builder.get_object('minimap_icon')
		self.window.bottom_panel_box.add(self.bottom_panel)
		self.implements_panel = True
		# self.needed_width_for_long = XXX TODO currently harcoded
		self.needed_width_for_long = 450