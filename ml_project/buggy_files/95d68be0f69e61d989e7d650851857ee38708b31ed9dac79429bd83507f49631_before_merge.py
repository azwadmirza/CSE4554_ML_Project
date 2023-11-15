def update(device, need_popup=False):
	if _window is None:
		return

	assert device is not None

	if need_popup:
		popup()

	selected_device_id = _find_selected_device_id()

	if device.kind is None:
		# receiver
		is_alive = bool(device)
		item = _receiver_row(device.path, device if is_alive else None)
		assert item

		if is_alive and item:
			was_pairing = bool(_model.get_value(item, _COLUMN.STATUS_ICON))
			is_pairing = bool(device.status.lock_open)
			_model.set_value(item, _COLUMN.STATUS_ICON, 'network-wireless' if is_pairing else _CAN_SET_ROW_NONE)

			if selected_device_id == (device.path, 0):
				full_update = need_popup or was_pairing != is_pairing
				_update_info_panel(device, full=full_update)

		elif item:
			if _TREE_SEPATATOR:
				separator = _model.iter_next(item)
				_model.remove(separator)
			_model.remove(item)

	else:
		# peripheral
		is_paired = bool(device)
		assert device.receiver
		assert device.number is not None and device.number > 0, "invalid device number" + str(device.number)
		item = _device_row(device.receiver.path, device.number, device if is_paired else None)

		if is_paired and item:
			was_online = _model.get_value(item, _COLUMN.ACTIVE)
			is_online = bool(device.online)
			_model.set_value(item, _COLUMN.ACTIVE, is_online)

			battery_level = device.status.get(_K.BATTERY_LEVEL)
			if battery_level is None:
				_model.set_value(item, _COLUMN.STATUS_TEXT, _CAN_SET_ROW_NONE)
				_model.set_value(item, _COLUMN.STATUS_ICON, _CAN_SET_ROW_NONE)
			else:
				if isinstance(battery_level, _NamedInt):
					status_text = _("%(battery_level)s") % { 'battery_level': _(str(battery_level)) }
				else:
					status_text = _("%(battery_percent)d%%") % { 'battery_percent': battery_level }
				_model.set_value(item, _COLUMN.STATUS_TEXT, status_text)

				charging = device.status.get(_K.BATTERY_CHARGING)
				icon_name = _icons.battery(battery_level, charging)
				_model.set_value(item, _COLUMN.STATUS_ICON, icon_name)

			if selected_device_id is None or need_popup:
				select(device.receiver.path, device.number)
			elif selected_device_id == (device.receiver.path, device.number):
				full_update = need_popup or was_online != is_online
				_update_info_panel(device, full=full_update)

		elif item:
			_model.remove(item)
			_config_panel.clean(device)

	# make sure all rows are visible
	_tree.expand_all()