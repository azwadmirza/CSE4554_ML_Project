def _unpack_json_args(args):
    """Restore arguments from --json-args after a restart.

    When restarting, we serialize the argparse namespace into json, and
    construct a "fake" argparse.Namespace here based on the data loaded
    from json.
    """
    data = json.loads(args.json_args)
    return argparse.Namespace(**data)