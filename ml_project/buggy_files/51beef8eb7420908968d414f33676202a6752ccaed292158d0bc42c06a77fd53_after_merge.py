  def _ProcessPathSpec(self, path_spec):
    """Processes a path specification.

    Args:
      path_spec: A path specification object (instance of dfvfs.PathSpec).
    """
    try:
      file_entry = path_spec_resolver.Resolver.OpenFileEntry(
          path_spec, resolver_context=self._resolver_context)

      if file_entry is None:
        logging.warning(
            u'Unable to open file entry with path spec: {0:s}'.format(
                path_spec.comparable))
        return

      self._ProcessFileEntry(file_entry)

    except IOError as exception:
      logging.warning(
          u'Unable to process path spec: {0:s} with error: {1:s}'.format(
              path_spec.comparable, exception))

    except dfvfs_errors.CacheFullError:
      # TODO: signal engine of failure.
      self._abort = True
      logging.error((
          u'ABORT: detected cache full error while processing '
          u'path spec: {0:s}').format(path_spec.comparable))

    # All exceptions need to be caught here to prevent the worker
    # form being killed by an uncaught exception.
    except Exception as exception:
      logging.warning(
          u'Unhandled exception while processing path spec: {0:s}.'.format(
              path_spec.comparable))
      logging.exception(exception)
      # TODO: Issue #314 - add a signal to the worker to indicate that
      # the tool is run in single process mode with debug turned on and
      # in that case start a pdb debugger here instead of just logging
      # the exception.

    # Make sure frame.f_locals does not keep a reference to file_entry.
    file_entry = None