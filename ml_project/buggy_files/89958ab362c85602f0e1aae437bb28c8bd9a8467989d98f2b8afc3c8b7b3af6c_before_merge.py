    def keyPressEvent(self, event):
        """ Process key press events and match with known shortcuts"""
        # Detect the current KeySequence pressed (including modifier keys)
        key_value = event.key()
        modifiers = int(event.modifiers())

        # Abort handling if the key sequence is invalid
        if (key_value <= 0 or key_value in
           [Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Control, Qt.Key_Meta]):
            return

        # A valid keysequence was detected
        event.accept()
        key = QKeySequence(modifiers + key_value)

        # Get the video player object
        player = self.preview_thread.player

        # Get framerate
        fps = get_app().project.get("fps")
        fps_float = float(fps["num"]) / float(fps["den"])
        playhead_position = float(self.preview_thread.current_frame - 1) / fps_float

        # Basic shortcuts i.e just a letter
        if key.matches(self.getShortcutByName("seekPreviousFrame")) == QKeySequence.ExactMatch:
            # Pause video
            self.actionPlay_trigger(force="pause")
            # Set speed to 0
            if player.Speed() != 0:
                self.SpeedSignal.emit(0)
            # Seek to previous frame
            self.SeekSignal.emit(player.Position() - 1)

            # Notify properties dialog
            self.propertyTableView.select_frame(player.Position())

        elif key.matches(self.getShortcutByName("seekNextFrame")) == QKeySequence.ExactMatch:
            # Pause video
            self.actionPlay_trigger(force="pause")
            # Set speed to 0
            if player.Speed() != 0:
                self.SpeedSignal.emit(0)
            # Seek to next frame
            self.SeekSignal.emit(player.Position() + 1)

            # Notify properties dialog
            self.propertyTableView.select_frame(player.Position())

        elif key.matches(self.getShortcutByName("rewindVideo")) == QKeySequence.ExactMatch:
            # Toggle rewind and start playback
            self.actionRewind.trigger()
            ui_util.setup_icon(self, self.actionPlay, "actionPlay", "media-playback-pause")
            self.actionPlay.setChecked(True)

        elif key.matches(self.getShortcutByName("fastforwardVideo")) == QKeySequence.ExactMatch:
            # Toggle fastforward button and start playback
            self.actionFastForward.trigger()
            ui_util.setup_icon(self, self.actionPlay, "actionPlay", "media-playback-pause")
            self.actionPlay.setChecked(True)

        elif any([
                key.matches(self.getShortcutByName("playToggle")) == QKeySequence.ExactMatch,
                key.matches(self.getShortcutByName("playToggle1")) == QKeySequence.ExactMatch,
                key.matches(self.getShortcutByName("playToggle2")) == QKeySequence.ExactMatch,
                key.matches(self.getShortcutByName("playToggle3")) == QKeySequence.ExactMatch,
                ]):
            # Toggle playbutton and show properties
            self.actionPlay.trigger()
            self.propertyTableView.select_frame(player.Position())

        elif any([
                key.matches(self.getShortcutByName("deleteItem")) == QKeySequence.ExactMatch,
                key.matches(self.getShortcutByName("deleteItem1")) == QKeySequence.ExactMatch,
                ]):
            # Delete selected clip / transition
            self.actionRemoveClip.trigger()
            self.actionRemoveTransition.trigger()

        # Menu shortcuts
        elif key.matches(self.getShortcutByName("actionNew")) == QKeySequence.ExactMatch:
            self.actionNew.trigger()
        elif key.matches(self.getShortcutByName("actionOpen")) == QKeySequence.ExactMatch:
            self.actionOpen.trigger()
        elif key.matches(self.getShortcutByName("actionSave")) == QKeySequence.ExactMatch:
            self.actionSave.trigger()
        elif key.matches(self.getShortcutByName("actionUndo")) == QKeySequence.ExactMatch:
            self.actionUndo.trigger()
        elif key.matches(self.getShortcutByName("actionSaveAs")) == QKeySequence.ExactMatch:
            self.actionSaveAs.trigger()
        elif key.matches(self.getShortcutByName("actionImportFiles")) == QKeySequence.ExactMatch:
            self.actionImportFiles.trigger()
        elif key.matches(self.getShortcutByName("actionRedo")) == QKeySequence.ExactMatch:
            self.actionRedo.trigger()
        elif key.matches(self.getShortcutByName("actionExportVideo")) == QKeySequence.ExactMatch:
            self.actionExportVideo.trigger()
        elif key.matches(self.getShortcutByName("actionQuit")) == QKeySequence.ExactMatch:
            self.actionQuit.trigger()
        elif key.matches(self.getShortcutByName("actionPreferences")) == QKeySequence.ExactMatch:
            self.actionPreferences.trigger()
        elif key.matches(self.getShortcutByName("actionAddTrack")) == QKeySequence.ExactMatch:
            self.actionAddTrack.trigger()
        elif key.matches(self.getShortcutByName("actionAddMarker")) == QKeySequence.ExactMatch:
            self.actionAddMarker.trigger()
        elif key.matches(self.getShortcutByName("actionPreviousMarker")) == QKeySequence.ExactMatch:
            self.actionPreviousMarker.trigger()
        elif key.matches(self.getShortcutByName("actionNextMarker")) == QKeySequence.ExactMatch:
            self.actionNextMarker.trigger()
        elif key.matches(self.getShortcutByName("actionCenterOnPlayhead")) == QKeySequence.ExactMatch:
            self.actionCenterOnPlayhead.trigger()
        elif key.matches(self.getShortcutByName("actionTimelineZoomIn")) == QKeySequence.ExactMatch:
            self.actionTimelineZoomIn.trigger()
        elif key.matches(self.getShortcutByName("actionTimelineZoomOut")) == QKeySequence.ExactMatch:
            self.actionTimelineZoomOut.trigger()
        elif key.matches(self.getShortcutByName("actionTitle")) == QKeySequence.ExactMatch:
            self.actionTitle.trigger()
        elif key.matches(self.getShortcutByName("actionAnimatedTitle")) == QKeySequence.ExactMatch:
            self.actionAnimatedTitle.trigger()
        elif key.matches(self.getShortcutByName("actionDuplicateTitle")) == QKeySequence.ExactMatch:
            self.actionDuplicateTitle.trigger()
        elif key.matches(self.getShortcutByName("actionEditTitle")) == QKeySequence.ExactMatch:
            self.actionEditTitle.trigger()
        elif key.matches(self.getShortcutByName("actionFullscreen")) == QKeySequence.ExactMatch:
            self.actionFullscreen.trigger()
        elif key.matches(self.getShortcutByName("actionAbout")) == QKeySequence.ExactMatch:
            self.actionAbout.trigger()
        elif key.matches(self.getShortcutByName("actionThumbnailView")) == QKeySequence.ExactMatch:
            self.actionThumbnailView.trigger()
        elif key.matches(self.getShortcutByName("actionDetailsView")) == QKeySequence.ExactMatch:
            self.actionDetailsView.trigger()
        elif key.matches(self.getShortcutByName("actionProfile")) == QKeySequence.ExactMatch:
            self.actionProfile.trigger()
        elif key.matches(self.getShortcutByName("actionAdd_to_Timeline")) == QKeySequence.ExactMatch:
            self.actionAdd_to_Timeline.trigger()
        elif key.matches(self.getShortcutByName("actionSplitClip")) == QKeySequence.ExactMatch:
            self.actionSplitClip.trigger()
        elif key.matches(self.getShortcutByName("actionSnappingTool")) == QKeySequence.ExactMatch:
            self.actionSnappingTool.trigger()
        elif key.matches(self.getShortcutByName("actionJumpStart")) == QKeySequence.ExactMatch:
            self.actionJumpStart.trigger()
        elif key.matches(self.getShortcutByName("actionJumpEnd")) == QKeySequence.ExactMatch:
            self.actionJumpEnd.trigger()
        elif key.matches(self.getShortcutByName("actionSaveFrame")) == QKeySequence.ExactMatch:
            self.actionSaveFrame.trigger()
        elif key.matches(self.getShortcutByName("actionProperties")) == QKeySequence.ExactMatch:
            self.actionProperties.trigger()
        elif key.matches(self.getShortcutByName("actionTransform")) == QKeySequence.ExactMatch:
            if self.selected_clips:
                self.TransformSignal.emit(self.selected_clips[0])
        elif key.matches(self.getShortcutByName("actionInsertKeyframe")) == QKeySequence.ExactMatch:
            log.debug("actionInsertKeyframe")
            if self.selected_clips or self.selected_transitions:
                self.InsertKeyframe.emit(event)

        # Timeline keyboard shortcuts
        elif key.matches(self.getShortcutByName("sliceAllKeepBothSides")) == QKeySequence.ExactMatch:
            intersecting_clips = Clip.filter(intersect=playhead_position)
            intersecting_trans = Transition.filter(intersect=playhead_position)
            if intersecting_clips or intersecting_trans:
                # Get list of clip ids
                clip_ids = [c.id for c in intersecting_clips]
                trans_ids = [t.id for t in intersecting_trans]
                self.timeline.Slice_Triggered(0, clip_ids, trans_ids, playhead_position)
        elif key.matches(self.getShortcutByName("sliceAllKeepLeftSide")) == QKeySequence.ExactMatch:
            intersecting_clips = Clip.filter(intersect=playhead_position)
            intersecting_trans = Transition.filter(intersect=playhead_position)
            if intersecting_clips or intersecting_trans:
                # Get list of clip ids
                clip_ids = [c.id for c in intersecting_clips]
                trans_ids = [t.id for t in intersecting_trans]
                self.timeline.Slice_Triggered(1, clip_ids, trans_ids, playhead_position)
        elif key.matches(self.getShortcutByName("sliceAllKeepRightSide")) == QKeySequence.ExactMatch:
            intersecting_clips = Clip.filter(intersect=playhead_position)
            intersecting_trans = Transition.filter(intersect=playhead_position)
            if intersecting_clips or intersecting_trans:
                # Get list of clip ids
                clip_ids = [c.id for c in intersecting_clips]
                trans_ids = [t.id for t in intersecting_trans]
                self.timeline.Slice_Triggered(2, clip_ids, trans_ids, playhead_position)
        elif key.matches(self.getShortcutByName("sliceSelectedKeepBothSides")) == QKeySequence.ExactMatch:
            intersecting_clips = Clip.filter(intersect=playhead_position)
            intersecting_trans = Transition.filter(intersect=playhead_position)
            if intersecting_clips or intersecting_trans:
                # Get list of clip ids
                clip_ids = [c.id for c in intersecting_clips if c.id in self.selected_clips]
                trans_ids = [t.id for t in intersecting_trans if t.id in self.selected_transitions]
                self.timeline.Slice_Triggered(0, clip_ids, trans_ids, playhead_position)
        elif key.matches(self.getShortcutByName("sliceSelectedKeepLeftSide")) == QKeySequence.ExactMatch:
            intersecting_clips = Clip.filter(intersect=playhead_position)
            intersecting_trans = Transition.filter(intersect=playhead_position)
            if intersecting_clips or intersecting_trans:
                # Get list of clip ids
                clip_ids = [c.id for c in intersecting_clips if c.id in self.selected_clips]
                trans_ids = [t.id for t in intersecting_trans if t.id in self.selected_transitions]
                self.timeline.Slice_Triggered(1, clip_ids, trans_ids, playhead_position)
        elif key.matches(self.getShortcutByName("sliceSelectedKeepRightSide")) == QKeySequence.ExactMatch:
            intersecting_clips = Clip.filter(intersect=playhead_position)
            intersecting_trans = Transition.filter(intersect=playhead_position)
            if intersecting_clips or intersecting_trans:
                # Get list of ids that are also selected
                clip_ids = [c.id for c in intersecting_clips if c.id in self.selected_clips]
                trans_ids = [t.id for t in intersecting_trans if t.id in self.selected_transitions]
                self.timeline.Slice_Triggered(2, clip_ids, trans_ids, playhead_position)

        elif key.matches(self.getShortcutByName("copyAll")) == QKeySequence.ExactMatch:
            self.timeline.Copy_Triggered(-1, self.selected_clips, self.selected_transitions)
        elif key.matches(self.getShortcutByName("pasteAll")) == QKeySequence.ExactMatch:
            self.timeline.Paste_Triggered(9, float(playhead_position), -1, [], [])
        elif key.matches(self.getShortcutByName("nudgeLeft")) == QKeySequence.ExactMatch:
            self.timeline.Nudge_Triggered(-1, self.selected_clips, self.selected_transitions)
        elif key.matches(self.getShortcutByName("nudgeRight")) == QKeySequence.ExactMatch:
            self.timeline.Nudge_Triggered(1, self.selected_clips, self.selected_transitions)

        # Select All / None
        elif key.matches(self.getShortcutByName("selectAll")) == QKeySequence.ExactMatch:
            self.timeline.SelectAll()

        elif key.matches(self.getShortcutByName("selectNone")) == QKeySequence.ExactMatch:
            self.timeline.ClearAllSelections()

        # If we didn't act on the event, forward it to the base class
        else:
            QMainWindow.keyPressEvent(self, event)