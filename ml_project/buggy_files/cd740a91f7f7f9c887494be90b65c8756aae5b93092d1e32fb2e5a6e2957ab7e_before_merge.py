  def ExamineEvent(self, analysis_mediator, event_object, **kwargs):
    """Analyzes an EventObject and tags it according to rules in the tag file.

    Args:
      analysis_mediator: The analysis mediator object (instance of
                         AnalysisMediator).
      event_object: The event object (instance of EventObject) to examine.
    """
    if self._tag_rules is None:
      if self._autodetect_tag_file_attempt:
        # There's nothing to tag with, and we've already tried to find a good
        # tag file, so there's nothing we can do with this event (or any other).
        return
      if not self._AttemptAutoDetectTagFile(analysis_mediator):
        return

    matched_tags = []
    for tag, my_filters in self._tag_rules.iteritems():
      for my_filter in my_filters:
        if my_filter.Match(event_object):
          matched_tags.append(tag)
          break
    if not matched_tags:
      return
    event_tag = event.EventTag()
    event_tag.event_uuid = getattr(event_object, u'uuid')
    event_tag.comment = u'Tag applied by tagging analysis plugin.'
    event_tag.tags = matched_tags
    self._tags.append(event_tag)