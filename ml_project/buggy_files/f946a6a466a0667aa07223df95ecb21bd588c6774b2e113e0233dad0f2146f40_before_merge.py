    def destroy(self):
        for name in 'jobItems', 'jobFileIDs', 'files', 'statsFiles', 'statsFileIDs':
            resource = getattr(self, name)
            if resource is not None:
                if isinstance(resource, AzureTable):
                    resource.delete_table()
                elif isinstance(resource, AzureBlobContainer):
                    resource.delete_container()
                else:
                    assert False
                setattr(self, name, None)