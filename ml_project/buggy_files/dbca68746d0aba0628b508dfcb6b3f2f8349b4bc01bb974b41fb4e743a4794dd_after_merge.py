    def closeEvent(self, event):

        app = get_app()
        # Some window managers handels dragging of the modal messages incorrectly if other windows are open
        # Hide tutorial window first
        self.tutorial_manager.hide_dialog()

        # Prompt user to save (if needed)
        if app.project.needs_save() and self.mode != "unittest":
            log.info('Prompt user to save project')
            # Translate object
            _ = app._tr

            # Handle exception
            ret = QMessageBox.question(
                self,
                _("Unsaved Changes"),
                _("Save changes to project before closing?"),
                QMessageBox.Cancel | QMessageBox.No | QMessageBox.Yes)
            if ret == QMessageBox.Yes:
                # Save project
                self.actionSave_trigger()
                event.accept()
            elif ret == QMessageBox.Cancel:
                # Show tutorial again, if any
                self.tutorial_manager.re_show_dialog()
                # User canceled prompt - don't quit
                event.ignore()
                return

        # Log the exit routine
        log.info('---------------- Shutting down -----------------')

        # Close any tutorial dialogs
        self.tutorial_manager.exit_manager()

        # Save settings
        self.save_settings()

        # Track end of session
        track_metric_session(False)

        # Stop threads
        self.StopSignal.emit()

        # Process any queued events
        QCoreApplication.processEvents()

        # Stop preview thread (and wait for it to end)
        self.preview_thread.player.CloseAudioDevice()
        self.preview_thread.kill()
        self.preview_parent.background.exit()
        self.preview_parent.background.wait(5000)

        # Close Timeline
        self.timeline_sync.timeline.Close()
        self.timeline_sync.timeline = None

        # Destroy lock file
        self.destroy_lock_file()