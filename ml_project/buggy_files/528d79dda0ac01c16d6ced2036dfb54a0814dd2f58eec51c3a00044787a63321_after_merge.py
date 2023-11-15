  def add_functionary_key(self, key):
    """
    <Purpose>
      Add the passed functionary public key to the layout's dictionary of keys.

    <Arguments>
      key:
              A functionary public key conformant with
              securesystemslib.formats.ANY_PUBKEY_SCHEMA.

    <Exceptions>
      securesystemslib.exceptions.FormatError
              If the passed key does not match
              securesystemslib.formats.ANY_PUBKEY_SCHEMA.

    <Returns>
      The added functionary public key.

    """
    securesystemslib.formats.ANY_PUBKEY_SCHEMA.check_match(key)
    keyid = key["keyid"]
    self.keys[keyid] = key
    return key