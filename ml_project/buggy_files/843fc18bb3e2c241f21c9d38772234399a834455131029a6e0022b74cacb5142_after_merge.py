    def close_tribler(self):
        if not self.core_manager.shutting_down:
            if self.tray_icon:
                self.tray_icon.deleteLater()
            self.show_loading_screen()
            self.loading_text_label.setText("Shutting down...")

            self.gui_settings.setValue("pos", self.pos())
            self.gui_settings.setValue("size", self.size())

            if self.core_manager.use_existing_core:
                # Don't close the core that we are using
                QApplication.quit()

            self.core_manager.stop()
            self.core_manager.shutting_down = True
            self.downloads_page.stop_loading_downloads()
            request_queue.clear()