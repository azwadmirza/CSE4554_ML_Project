def is_comment_signed_by_channel(comment: dict, channel: Output):
    if type(channel) is Output:
        try:
            pieces = [
                comment['signing_ts'].encode(),
                channel.claim_hash,
                comment['comment'].encode()
            ]
            return Output.is_signature_valid(
                get_encoded_signature(comment['signature']),
                sha256(b''.join(pieces)),
                channel.claim.channel.public_key_bytes
            )
        except KeyError:
            pass
    return False