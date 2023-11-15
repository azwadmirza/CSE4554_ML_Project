def pack_rule(rule_type, pattern, source_prefix=None, dest_type=None,
      dest_prefix=None, dest_name=None):
  """
  <Purpose>
    Create an artifact rule in the passed arguments and return it as list
    as it is stored in a step's or inspection's expected_material or
    expected_product field.

  <Arguments>
    rule_type:
            One of "MATCH", "CREATE", "DELETE", MODIFY, ALLOW, DISALLOW,
            REQUIRE (case insensitive).

    pattern:
            A glob pattern to match artifact paths.

    source_prefix: (only for "MATCH" rules)
            A prefix for 'pattern' to match artifacts reported by the link
            corresponding to the step that contains the rule.

    dest_type: (only for "MATCH" rules)
            One of "MATERIALS" or "PRODUCTS" (case insensitive) to specify
            if materials or products of the link corresponding to the step
            identified by 'dest_name' should be matched.

    dest_prefix: (only for "MATCH" rules)
            A prefix for 'pattern' to match artifacts reported by the link
            corresponding to the step identified by 'dest_name'.

    dest_name: (only for "MATCH" rules)
            The name of the step whose corresponding link is used to match
            artifacts.


  <Exceptions>
    securesystemslib.exceptions.FormatError
            if any of the arguments is malformed.


  <Returns>
    One of the following rule formats in as a list
      MATCH <pattern> [IN <source-path-prefix>] WITH (MATERIALS|PRODUCTS)
          [IN <destination-path-prefix>] FROM <step>,
      CREATE <pattern>,
      DELETE <pattern>,
      MODIFY <pattern>,
      ALLOW <pattern>,
      DISALLOW <pattern>,
      REQUIRE <file>

    Note that REQUIRE is somewhat of a weird animal that does not use patterns
    but rather single filenames (for now).
  """
  in_toto.formats.ANY_STRING_SCHEMA.check_match(rule_type)
  in_toto.formats.ANY_STRING_SCHEMA.check_match(pattern)

  if rule_type.lower() not in ALL_RULES:
    raise securesystemslib.exceptions.FormatError("'{0}' is not a valid "
        "'type'.  Rule type must be one of:  {1} (case insensitive)."
        .format(rule_type, ", ".join(ALL_RULES)))

  if rule_type.upper() == "MATCH":
    if (not in_toto.formats.ANY_STRING_SCHEMA.matches(dest_type) or not
        (dest_type.lower() == "materials" or dest_type.lower() == "products")):
      raise securesystemslib.exceptions.FormatError("'{}' is not a valid"
          " 'dest_type'. Rules of type 'MATCH' require a destination type of"
          " either 'MATERIALS' or 'PRODUCTS' (case insensitive)."
          .format(dest_type))

    if not (in_toto.formats.ANY_STRING_SCHEMA.matches(dest_name) and
        dest_name):
      raise securesystemslib.exceptions.FormatError("'{}' is not a valid"
          " 'dest_name'. Rules of type 'MATCH' require a step name as a"
          " destination name.".format(dest_name))

    # Construct rule
    rule = ["MATCH", pattern]

    if source_prefix:
      in_toto.formats.ANY_STRING_SCHEMA.check_match(source_prefix)
      rule += ["IN", source_prefix]

    rule += ["WITH", dest_type.upper()]

    if dest_prefix:
      in_toto.formats.ANY_STRING_SCHEMA.check_match(dest_prefix)
      rule += ["IN", dest_prefix]

    rule += ["FROM", dest_name]

  else:
    rule = [rule_type.upper(), pattern]

  return rule