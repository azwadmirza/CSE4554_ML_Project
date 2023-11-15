        def on_export_download_dialog_done(action):
            if action == 0:
                dest_path = os.path.join(export_dir, dialog.dialog_widget.dialog_input.text())
                request_mgr = TriblerRequestManager()
                request_mgr.download_file("mychannel/export",
                                          lambda data: on_export_download_request_done(dest_path, data))

            dialog.close_dialog()