    def handle_remote(self, job, upload=True):
        """ Remove local files if they are no longer needed and upload. """
        if upload:
            # handle output files
            files = list(job.expanded_output)
            if job.benchmark:
                files.append(job.benchmark)
            for f in files:
                if f.is_remote and not f.should_stay_on_remote:
                    f.upload_to_remote()
                    remote_mtime = f.mtime
                    # immediately force local mtime to match remote,
                    # since conversions from S3 headers are not 100% reliable
                    # without this, newness comparisons may fail down the line
                    f.touch(times=(remote_mtime, remote_mtime))

                    if not f.exists_remote:
                        raise RemoteFileException(
                            "The file upload was attempted, but it does not "
                            "exist on remote. Check that your credentials have "
                            "read AND write permissions."
                        )

        if not self.keep_remote_local:
            # handle input files
            needed = lambda job_, f: any(
                f in files
                for j, files in self.depending[job_].items()
                if not self.finished(j) and self.needrun(j) and j != job
            )

            def unneeded_files():
                putative = (
                    lambda f: f.is_remote
                    and not f.protected
                    and not f.should_keep_local
                )
                generated_input = set()
                for job_, files in self.dependencies[job].items():
                    generated_input |= files
                    for f in filter(putative, files):
                        if not needed(job_, f):
                            yield f
                for f, f_ in zip(job.output, job.rule.output):
                    if putative(f) and not needed(job, f) and not f in self.targetfiles:
                        if f in job.dynamic_output:
                            for f_ in job.expand_dynamic(f_):
                                yield f_
                        else:
                            yield f
                for f in filter(putative, job.input):
                    # TODO what about remote inputs that are used by multiple jobs?
                    if f not in generated_input:
                        yield f

            for f in unneeded_files():
                if f.exists_local:
                    logger.info("Removing local output file: {}".format(f))
                    f.remove()