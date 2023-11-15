  def ParseRow(self, parser_mediator, row_offset, row):
    """Parse a line of the log file and extract event objects.

    Args:
      parser_mediator: a parser mediator object (instance of ParserMediator).
      row_offset: the offset of the row.
      row: a dictionary containing all the fields as denoted in the
           COLUMNS class list.
    """
    event_object = event.EventObject()
    if row_offset is not None:
      event_object.offset = row_offset
    event_object.row_dict = row
    parser_mediator.ProduceEvent(event_object)