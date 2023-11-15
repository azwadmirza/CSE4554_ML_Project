  def _validate_keys(self):
    """Private method to ensure that the keys contained are right."""
    in_toto.formats.ANY_PUBKEY_DICT_SCHEMA.check_match(self.keys)