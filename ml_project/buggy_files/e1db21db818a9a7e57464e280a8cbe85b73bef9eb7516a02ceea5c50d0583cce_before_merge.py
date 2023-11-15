  def verify_signature(self, verification_key):
    """
    <Purpose>
      Verifies the signature, found in `self.signatures`, corresponding to the
      passed verification key, or in case of GPG one of its subkeys, identified
      by the key's keyid, using the passed verification key and the utf-8
      encoded canonical JSON bytes of the Link or Layout object, contained in
      `self.signed`.

      If the signature matches `in_toto.gpg.formats.SIGNATURE_SCHEMA`,
      `in_toto.gpg.functions.gpg_verify_signature` is used for verification,
      if the signature matches `securesystemslib.formats.SIGNATURE_SCHEMA`
      `securesystemslib.keys.verify_signature` is used.

      Note: In case of securesystemslib we actually pass the dictionary
      representation of the data to be verified and
      `securesystemslib.keys.verify_signature` converts it to
      canonical JSON utf-8 encoded bytes before verifying the signature.

    <Arguments>
      verification_key:
              Verifying key in the format:
              in_toto.formats.ANY_VERIFICATION_KEY_SCHEMA

    <Exceptions>
      FormatError
            If the passed key is not conformant with
            `in_toto.formats.ANY_VERIFICATION_KEY_SCHEMA`

      SignatureVerificationError
            If the Metablock does not carry a signature signed with the
            private key corresponding to the passed verification key or one
            of its subkeys

            If the signature corresponding to the passed verification key or
            one of its subkeys does not match securesystemslib's or
            in_toto.gpg's signature schema.

            If the signature to be verified is malformed or invalid.

      in_toto.gpg.exceptions.KeyExpirationError:
            if the passed verification key is an expired gpg key

    <Returns>
      None.

    """
    in_toto.formats.ANY_VERIFICATION_KEY_SCHEMA.check_match(verification_key)
    verification_keyid = verification_key["keyid"]

    # Find a signature that corresponds to the keyid of the passed
    # verification key or one of its subkeys
    signature = None
    for signature in self.signatures:
      if signature["keyid"] == verification_keyid:
        break

      if signature["keyid"] in list(
          verification_key.get("subkeys", {}).keys()):
        break

    else:
      raise SignatureVerificationError("No signature found for key '{}'"
          .format(verification_keyid))

    if in_toto.gpg.formats.SIGNATURE_SCHEMA.matches(signature):
      valid = in_toto.gpg.functions.gpg_verify_signature(signature,
          verification_key, self.signed.signable_bytes)

    elif securesystemslib.formats.SIGNATURE_SCHEMA.matches(signature):
      valid = securesystemslib.keys.verify_signature(
          verification_key, signature, self.signed.signable_bytes)

    else:
      valid = False

    if not valid:
      raise SignatureVerificationError("Invalid signature for keyid '{}'"
          .format(verification_keyid))