  def _validate_signatures(self):
    """Private method to check that the 'signatures' attribute is a list of
    signatures in the format 'in_toto.formats.ANY_SIGNATURE_SCHEMA'. """

    if not isinstance(self.signatures, list):
      raise securesystemslib.exceptions.FormatError("The Metablock's"
        " 'signatures' property has to be of type 'list'.")

    for signature in self.signatures:
      in_toto.formats.ANY_SIGNATURE_SCHEMA.check_match(signature)