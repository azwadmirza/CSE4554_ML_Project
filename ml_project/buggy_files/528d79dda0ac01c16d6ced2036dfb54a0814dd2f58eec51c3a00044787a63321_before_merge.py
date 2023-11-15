  def add_functionary_key(self, key):
    """
    <Purpose>
      Add the passed functionary public key to the layout's dictionary of keys.

    <Arguments>
      key:
              A functionary public key conformant with
              in_toto.formats.ANY_PUBKEY_SCHEMA.

    <Exceptions>
      securesystemslib.exceptions.FormatError
              If the passed key does not match
              in_toto.formats.ANY_PUBKEY_SCHEMA.

    <Returns>
      The added functionary public key.

    """
    in_toto.formats.ANY_PUBKEY_SCHEMA.check_match(key)
    keyid = key["keyid"]
    self.keys[keyid] = key
    return key