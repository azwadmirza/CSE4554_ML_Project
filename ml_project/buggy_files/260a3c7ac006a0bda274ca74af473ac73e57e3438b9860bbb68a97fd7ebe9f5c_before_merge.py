    def _download_blob(blob_service, container, destination_folder, blob_name):
        import os
        # TODO: try catch IO exception
        destination_path = os.path.join(destination_folder, blob_name)
        destination_folder = os.path.dirname(destination_path)
        if not os.path.exists(destination_folder):
            mkdir_p(destination_folder)

        blob = blob_service.get_blob_to_path(container, blob_name, destination_path,
                                             progress_callback=progress_callback)
        return blob.name