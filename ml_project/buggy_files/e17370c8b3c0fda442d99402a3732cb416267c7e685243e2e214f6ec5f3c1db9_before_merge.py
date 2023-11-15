    def shutdown(self):
        """Shutdown kernel"""
        if self.get_kernel() is not None and not self.slave:
            self.shellwidget.spyder_kernel_comm.close()
            self.shellwidget.spyder_kernel_comm.shutdown_comm_channel()
            self.shellwidget._pdb_history_file.save_thread.stop()
            self.shellwidget.kernel_manager.stop_restarter()
        self.shutdown_thread = QThread()
        self.shutdown_thread.run = self.finalize_shutdown
        self.shutdown_thread.finished.connect(self.stop_kernel_channels)
        self.shutdown_thread.start()