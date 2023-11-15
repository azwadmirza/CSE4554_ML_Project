    def update(self, data):
        """
        Using the progress from Web, update the progress bar and file size labels
        for each file
        """
        if data['action'] == 'progress':
            total_uploaded_bytes = 0
            for filename in data['progress']:
                total_uploaded_bytes += data['progress'][filename]['uploaded_bytes']

            # Update the progress bar
            self.progress_bar.setMaximum(self.content_length)
            self.progress_bar.setValue(total_uploaded_bytes)

            elapsed = datetime.now() - self.started
            if elapsed.seconds < 10:
                pb_fmt = strings._('gui_all_modes_progress_starting').format(
                    self.common.human_readable_filesize(total_uploaded_bytes))
            else:
                estimated_time_remaining = self.common.estimated_time_remaining(
                    total_uploaded_bytes,
                    self.content_length,
                    self.started.timestamp())
                pb_fmt = strings._('gui_all_modes_progress_eta').format(
                    self.common.human_readable_filesize(total_uploaded_bytes),
                    estimated_time_remaining)

            # Using list(progress) to avoid "RuntimeError: dictionary changed size during iteration"
            for filename in list(data['progress']):
                # Add a new file if needed
                if filename not in self.files:
                    self.files[filename] = ReceiveHistoryItemFile(self.common, filename)
                    self.files_layout.addWidget(self.files[filename])

                # Update the file
                self.files[filename].update(data['progress'][filename]['uploaded_bytes'], data['progress'][filename]['complete'])

        elif data['action'] == 'rename':
            self.files[data['old_filename']].rename(data['new_filename'])
            self.files[data['new_filename']] = self.files.pop(data['old_filename'])

        elif data['action'] == 'set_dir':
            self.files[data['filename']].set_dir(data['dir'])

        elif data['action'] == 'finished':
            # Hide the progress bar
            self.progress_bar.hide()

            # Change the label
            self.label.setText(self.get_finished_label_text(self.started))

        elif data['action'] == 'canceled':
            # Hide the progress bar
            self.progress_bar.hide()

            # Change the label
            self.label.setText(self.get_canceled_label_text(self.started))