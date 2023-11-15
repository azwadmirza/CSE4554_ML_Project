    def _upload_dependencies_to_object_store(self, runtime_configuration, pipeline_name, operation):
        operation_artifact_archive = self._get_dependency_archive_name(operation)
        cos_directory = pipeline_name
        # upload operation dependencies to object store
        try:
            t0 = time.time()
            dependency_archive_path = self._generate_dependency_archive(operation)
            self.log_pipeline_info(pipeline_name,
                                   f"generated dependency archive: {dependency_archive_path}",
                                   operation_name=operation.name,
                                   duration=(time.time() - t0))

            cos_client = CosClient(config=runtime_configuration)

            t0 = time.time()
            cos_client.upload_file_to_dir(dir=cos_directory,
                                          file_name=operation_artifact_archive,
                                          file_path=dependency_archive_path)
            self.log_pipeline_info(pipeline_name,
                                   f"uploaded dependency archive to: {cos_directory}/{operation_artifact_archive}",
                                   operation_name=operation.name,
                                   duration=(time.time() - t0))

        except FileNotFoundError as ex:
            self.log.error("Dependencies were not found building archive for operation: {}".
                           format(operation.name), exc_info=True)
            raise FileNotFoundError("Node '{}' referenced dependencies that were not found: {}".
                                    format(operation.name, ex)) from ex
        except MaxRetryError as ex:
            cos_endpoint = runtime_configuration.metadata.get('cos_endpoint')
            self.log.error("Connection was refused when attempting to connect to : {}".
                           format(cos_endpoint), exc_info=True)
            raise RuntimeError("Connection was refused when attempting to upload artifacts to : '{}'. Please "
                               "check your object storage settings. ".format(cos_endpoint)) from ex
        except BaseException as ex:
            self.log.error("Error uploading artifacts to object storage for operation: {}".
                           format(operation.name), exc_info=True)
            raise ex from ex