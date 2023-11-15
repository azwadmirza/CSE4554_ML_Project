def decode(filename, ignore_bad_template):
    """
        Decode filename into an object
    """
    template = None
    matches = []
    try:
        template = cfnlint.decode.cfn_yaml.load(filename)
    except IOError as e:
        if e.errno == 2:
            LOGGER.error('Template file not found: %s', filename)
            matches.append(create_match_file_error(filename, 'Template file not found: %s' % filename))
        elif e.errno == 21:
            LOGGER.error('Template references a directory, not a file: %s', filename)
            matches.append(create_match_file_error(filename, 'Template references a directory, not a file: %s' % filename))
        elif e.errno == 13:
            LOGGER.error('Permission denied when accessing template file: %s', filename)
            matches.append(create_match_file_error(filename, 'Permission denied when accessing template file: %s' % filename))

        if matches:
            return(None, matches)
    except UnicodeDecodeError as err:
        LOGGER.error('Cannot read file contents: %s', filename)
        matches.append(create_match_file_error(filename, 'Cannot read file contents: %s' % filename))
    except cfnlint.decode.cfn_yaml.CfnParseError as err:
        err.match.Filename = filename
        matches = [err.match]

    except ParserError as err:
        matches = [create_match_yaml_parser_error(err, filename)]
    except ScannerError as err:
        if err.problem == 'found character \'\\t\' that cannot start any token':
            try:
                with open(filename) as fp:
                    template = json.load(fp, cls=cfnlint.decode.cfn_json.CfnJSONDecoder)
            except cfnlint.decode.cfn_json.JSONDecodeError as json_err:
                json_err.match.filename = filename
                matches = [json_err.match]
            except JSONDecodeError as json_err:
                matches = [create_match_json_parser_error(json_err, filename)]
            except Exception as json_err:  # pylint: disable=W0703
                if ignore_bad_template:
                    LOGGER.info('Template %s is malformed: %s', filename, err.problem)
                    LOGGER.info('Tried to parse %s as JSON but got error: %s', filename, str(json_err))
                else:
                    LOGGER.error('Template %s is malformed: %s', filename, err.problem)
                    LOGGER.error('Tried to parse %s as JSON but got error: %s', filename, str(json_err))
                    return(None, [create_match_file_error(filename, 'Tried to parse %s as JSON but got error: %s' % (filename, str(json_err)))])
        else:
            matches = [create_match_yaml_parser_error(err, filename)]
    except YAMLError as err:
        matches = [create_match_file_error(filename, err)]

    if not isinstance(template, dict) and not matches:
        # Template isn't a dict which means nearly nothing will work
        matches = [cfnlint.Match(1, 1, 1, 1, filename, cfnlint.ParseError(), message='Template needs to be an object.')]
    return (template, matches)