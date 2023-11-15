    def safe_run(self, manifest):
        catchable_errors = (dbt.exceptions.CompilationException,
                            dbt.exceptions.RuntimeException)

        result = RunModelResult(self.node)
        started = time.time()
        exc_info = (None, None, None)

        try:
            # if we fail here, we still have a compiled node to return
            # this has the benefit of showing a build path for the errant model
            compiled_node = self.compile(manifest)
            result.node = compiled_node

            # for ephemeral nodes, we only want to compile, not run
            if not self.is_ephemeral_model(self.node):
                result = self.run(compiled_node, manifest)

        except catchable_errors as e:
            if e.node is None:
                e.node = result.node

            result.error = dbt.compat.to_string(e)
            result.status = 'ERROR'

        except dbt.exceptions.InternalException as e:
            build_path = self.node.build_path
            prefix = 'Internal error executing {}'.format(build_path)

            error = "{prefix}\n{error}\n\n{note}".format(
                         prefix=dbt.ui.printer.red(prefix),
                         error=str(e).strip(),
                         note=INTERNAL_ERROR_STRING)
            logger.debug(error)

            result.error = dbt.compat.to_string(e)
            result.status = 'ERROR'

        except Exception as e:
            # set this here instead of finally, as python 2/3 exc_info()
            # behavior with re-raised exceptions are slightly different
            exc_info = sys.exc_info()
            prefix = "Unhandled error while executing {filepath}".format(
                        filepath=self.node.build_path)

            error = "{prefix}\n{error}".format(
                         prefix=dbt.ui.printer.red(prefix),
                         error=str(e).strip())

            logger.error(error)
            raise e

        finally:
            exc_str = self._safe_release_connection()

            # if we had an unhandled exception, re-raise it
            if exc_info and exc_info[1]:
                six.reraise(*exc_info)

            # if releasing failed and the result doesn't have an error yet, set
            # an error
            if exc_str is not None and result.error is None:
                result.error = exc_str
                result.status = 'ERROR'

        result.execution_time = time.time() - started
        return result