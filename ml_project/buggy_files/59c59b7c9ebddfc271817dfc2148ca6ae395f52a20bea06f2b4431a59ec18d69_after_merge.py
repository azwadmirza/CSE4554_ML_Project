def parse_args(argv: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    argv = sys.argv[1:] if argv is None else list(argv)
    remapped_deprecated_args = []
    for index, arg in enumerate(argv):
        if arg in DEPRECATED_SINGLE_DASH_ARGS:
            remapped_deprecated_args.append(arg)
            argv[index] = f"-{arg}"

    parser = _build_arg_parser()
    arguments = {key: value for key, value in vars(parser.parse_args(argv)).items() if value}
    if remapped_deprecated_args:
        arguments["remapped_deprecated_args"] = remapped_deprecated_args
    if "dont_order_by_type" in arguments:
        arguments["order_by_type"] = False
        del arguments["dont_order_by_type"]
    multi_line_output = arguments.get("multi_line_output", None)
    if multi_line_output:
        if multi_line_output.isdigit():
            arguments["multi_line_output"] = WrapModes(int(multi_line_output))
        else:
            arguments["multi_line_output"] = WrapModes[multi_line_output]
    return arguments