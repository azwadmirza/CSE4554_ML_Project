    def _load_recorded_calibrations(self):
        notifications = fm.load_pldata_file(self._rec_dir, "notify")
        for topic, data in zip(notifications.topics, notifications.data):
            if topic == "notify.calibration.calibration_data":
                try:
                    calib_result = model.CalibrationResult(
                        mapping_plugin_name=data["mapper_name"],
                        # data["mapper_args"] is a fm.Frozen_Dict and causes
                        # https://github.com/pupil-labs/pupil/issues/1498
                        # if not converted to a normal dict
                        mapper_args=dict(data["mapper_args"]),
                    )
                except KeyError:
                    # notifications from old recordings will not have these fields!
                    continue
                mapping_method = "2d" if "2d" in data["calibration_method"] else "3d"
                # the unique id needs to be the same at every start or otherwise the
                # same calibrations would be added again and again. The timestamp is
                # the easiest datum that differs between calibrations but is the same
                # for every start
                unique_id = model.Calibration.create_unique_id_from_string(
                    str(data["timestamp"])
                )
                calibration = model.Calibration(
                    unique_id=unique_id,
                    name=make_unique.by_number_at_end(
                        "Recorded Calibration", self.item_names
                    ),
                    recording_uuid=self._recording_uuid,
                    mapping_method=mapping_method,
                    frame_index_range=self._get_recording_index_range(),
                    minimum_confidence=0.8,
                    is_offline_calibration=False,
                    result=calib_result,
                )
                self.add(calibration)