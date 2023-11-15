  def _SetTimezone(self, knowledge_base, timezone):
    """Sets the timezone in the knowledge base.

    Args:
      knowledge_base (KnowledgeBase): contains information from the source
          data needed for processing.
      timezone (str): timezone.
    """
    time_zone_str = knowledge_base.GetValue(u'time_zone_str')
    if time_zone_str:
      default_timezone = time_zone_str
    else:
      default_timezone = timezone

    if not default_timezone:
      default_timezone = u'UTC'

    logging.info(u'Setting timezone to: {0:s}'.format(default_timezone))

    try:
      knowledge_base.SetTimezone(default_timezone)
    except ValueError:
      logging.warning(
          u'Unsupported time zone: {0:s}, defaulting to {1:s}'.format(
              default_timezone, knowledge_base.timezone.zone))