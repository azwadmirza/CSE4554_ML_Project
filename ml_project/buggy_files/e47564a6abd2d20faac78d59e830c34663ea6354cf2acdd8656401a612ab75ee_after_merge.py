    def upload_package(self, package_reference, remote, retry, retry_wait, skip_upload=False):
        """Will upload the package to the first remote"""
        t1 = time.time()
        # existing package, will use short paths if defined
        package_folder = self._client_cache.package(package_reference, short_paths=None)
        # Get all the files in that directory
        files = gather_files(package_folder)

        self._output.rewrite_line("Checking package integrity...")
        if CONANINFO not in files or CONAN_MANIFEST not in files:
            logger.error("Missing info or manifest in uploading files: %s" % (str(files)))
            raise ConanException("Cannot upload corrupted package '%s'" % str(package_reference))

        logger.debug("====> Time remote_manager build_files_set : %f" % (time.time() - t1))

        # If package has been modified remove tgz to regenerate it
        read_manifest, expected_manifest = self._client_cache.package_manifests(package_reference)

        if read_manifest != expected_manifest:
            self._output.writeln("")
            diff = read_manifest.difference(expected_manifest)
            for fname, (h1, h2) in diff.items():
                self._output.warn("Mismatched checksum '%s' (manifest: %s, file: %s)"
                                  % (fname, h1, h2))

            if PACKAGE_TGZ_NAME in files:
                try:
                    tgz_path = os.path.join(package_folder, PACKAGE_TGZ_NAME)
                    os.unlink(tgz_path)
                except Exception:
                    pass
            error_msg = os.linesep.join("Mismatched checksum '%s' (manifest: %s, file: %s)"
                                        % (fname, h1, h2) for fname, (h1, h2) in diff.items())
            logger.error("Manifests doesn't match!\n%s" % error_msg)
            raise ConanException("Cannot upload corrupted package '%s'" % str(package_reference))
        else:
            self._output.rewrite_line("Package integrity OK!")
        self._output.writeln("")
        logger.debug("====> Time remote_manager check package integrity : %f" % (time.time() - t1))
        the_files = compress_package_files(files, package_folder, self._output)
        if not skip_upload:

            tmp = self._call_remote(remote, "upload_package", package_reference, the_files,
                                    retry, retry_wait)

            duration = time.time() - t1
            log_package_upload(package_reference, duration, the_files, remote)
            logger.debug("====> Time remote_manager upload_package: %f" % duration)
            return tmp
        else:
            return None