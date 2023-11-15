  def ParseRecord(self, parser_mediator, key, structure):
    """Parse a single extracted pyparsing structure.

    This function takes as an input a parsed pyparsing structure
    and produces an EventObject if possible from that structure.

    Args:
      parser_mediator: a parser mediator object (instance of ParserMediator).
      key: an identification string indicating the name of the parsed
           structure.
      structure: a pyparsing.ParseResults object from a line in the
                 log file.

    Returns:
      An event object (instance of EventObject) or None.
    """