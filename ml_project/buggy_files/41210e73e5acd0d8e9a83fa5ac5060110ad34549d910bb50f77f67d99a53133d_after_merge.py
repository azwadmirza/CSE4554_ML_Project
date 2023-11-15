def process_disable_cache(option, option_str, option_value, parser):
  setattr(parser.values, option.dest, None)