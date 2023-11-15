  def _HandleHashAnalysis(self, hash_analysis):
    """Deals with the results of the analysis of a hash.

    This method ensures that labels are generated for the hash,
    then tags all events derived from files with that hash.

    Args:
      hash_analysis (HashAnalysis): hash analysis plugin's results for a given
          hash.

    Returns:
      tuple: containing:

        list[dfvfs.PathSpec]: pathspecs that had the hash value looked up.
        list[str]: labels that corresponds to the hash value that was looked up.
        list[EventTag]: event tags for all events that were extracted from the
            path specifications.
    """
    tags = []
    labels = self.GenerateLabels(hash_analysis.hash_information)
    pathspecs = self._hash_pathspecs.pop(hash_analysis.subject_hash)
    for pathspec in pathspecs:
      event_uuids = self._event_uuids_by_pathspec.pop(pathspec)
      if labels:
        for event_uuid in event_uuids:
          tag = self._CreateTag(event_uuid, labels)
          tags.append(tag)
    return pathspecs, labels, tags