def warn_or_error(
  removal_version: str,
  deprecated_entity_description: str,
  hint: Optional[str] = None,
  deprecation_start_version: Optional[str] = None,
  stacklevel: int = 3,
  frame_info: Optional[inspect.FrameInfo] = None,
  ensure_stderr: bool = False,
  print_warning: bool = True,
) -> None:
  """Check the removal_version against the current pants version.

  Issues a warning if the removal version is > current pants version, or an error otherwise.

  :param removal_version: The pantsbuild.pants version at which the deprecated entity will
                          be/was removed.
  :param deprecated_entity_description: A short description of the deprecated entity, that
                                        we can embed in warning/error messages.
  :param hint: A message describing how to migrate from the removed entity.
  :param deprecation_start_version: The pantsbuild.pants version at which the entity will
                                    begin to display a deprecation warning. This must be less
                                    than the `removal_version`. If not provided, the
                                    deprecation warning is always displayed.
  :param stacklevel: The stacklevel to pass to warnings.warn, which determines the file name and
                     line number of the error message.
  :param frame_info: If provided, use this frame info instead of getting one from `stacklevel`.
  :param ensure_stderr: Whether use warnings.warn, or use warnings.showwarning to print
                        directly to stderr.
  :param print_warning: Whether to print a warning for deprecations *before* their removal.
                        If this flag is off, an exception will still be raised for options
                        past their deprecation date.
  :raises DeprecationApplicationError: if the removal_version parameter is invalid.
  :raises CodeRemovedError: if the current version is later than the version marked for removal.
  """
  removal_semver = validate_deprecation_semver(removal_version, 'removal version')
  if deprecation_start_version:
    deprecation_start_semver = validate_deprecation_semver(
      deprecation_start_version, 'deprecation start version')
    if deprecation_start_semver >= removal_semver:
      raise InvalidSemanticVersionOrderingError(
        'The deprecation start version {} must be less than the end version {}.'
        .format(deprecation_start_version, removal_version))
    elif PANTS_SEMVER < deprecation_start_semver:
      return

  msg = 'DEPRECATED: {} {} removed in version {}.'.format(deprecated_entity_description,
      get_deprecated_tense(removal_version), removal_version)
  if hint:
    msg += '\n  {}'.format(hint)

  # We need to have filename and line_number for warnings.formatwarning, which appears to be the only
  # way to get a warning message to display to stderr. We get that from frame_info.
  if frame_info is None:
    frame_info = _get_frame_info(stacklevel)
  _, filename, line_number, _, _, _ = frame_info

  if removal_semver > PANTS_SEMVER:
    if ensure_stderr:
      # No warning filters can stop us from printing this message directly to stderr.
      warning_msg = warnings.formatwarning(
        msg, DeprecationWarning, filename, line_number,
      )
      print(warning_msg, file=sys.stderr)
    elif print_warning:
      # This output is filtered by warning filters.
      warnings.warn_explicit(
        message=msg,
        category=DeprecationWarning,
        filename=filename,
        lineno=line_number,
      )
    return
  else:
    raise CodeRemovedError(msg)