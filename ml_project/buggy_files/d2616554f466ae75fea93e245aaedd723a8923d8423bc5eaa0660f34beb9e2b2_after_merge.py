    def upload(self):
        for root, dirs, files in os.walk(self.root_dir):
            for f in files:
                blob_name = self.join(self.file_prefix, root[len(self.root_dir):], f)
                blob_name.strip('/')
                try:
                    self.blob_service.create_blob_from_path(
                        self.container,
                        blob_name,
                        os.path.join(root, f))
                except AzureHttpError as e:
                    if e.status_code == 403:
                        self.log.error("Access Error: Storage Blob Data Contributor Role "
                                       "is required to write to Azure Blob Storage.")
                    else:
                        self.log.error("Error writing output. "
                                       "Confirm output storage URL is correct. \n" +
                                   str(e))

                self.log.debug("%s uploaded" % blob_name)