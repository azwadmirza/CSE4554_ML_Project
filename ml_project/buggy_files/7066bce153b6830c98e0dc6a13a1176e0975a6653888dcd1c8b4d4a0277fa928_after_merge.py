def import_gpg_public_keys_from_keyring_as_dict(keyids, gpg_home=False):
  """Creates a dictionary of gpg public keys retrieving gpg public keys
  identified by the list of passed `keyids` from the gpg keyring at `gpg_home`.
  If `gpg_home` is False the default keyring is used. """
  key_dict = {}
  for gpg_keyid in keyids:
    pub_key = securesystemslib.gpg.functions.export_pubkey(gpg_keyid,
        homedir=gpg_home)
    securesystemslib.formats.GPG_PUBKEY_SCHEMA.check_match(pub_key)
    keyid = pub_key["keyid"]
    key_dict[keyid] = pub_key
  return key_dict