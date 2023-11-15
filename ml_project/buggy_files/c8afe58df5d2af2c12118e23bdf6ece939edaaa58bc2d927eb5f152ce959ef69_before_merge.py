def custom_module_classes():
    """
    MultiQC Custom Content class. This module does a lot of different
    things depending on the input and is as flexible as possible.

    NB: THIS IS TOTALLY DIFFERENT TO ALL OTHER MODULES
    """

    # Dict to hold parsed data. Each key should contain a custom data type
    # eg. output from a particular script. Note that this script may pick
    # up many different types of data from many different sources.
    # Second level keys should be 'config' and 'data'. Data key should then
    # contain sample names, and finally data.
    cust_mods = defaultdict(lambda: defaultdict(lambda: OrderedDict()))

    # Dictionary to hold search patterns - start with those defined in the config
    search_patterns = ['custom_content']

    # First - find files using patterns described in the config
    config_data = getattr(config, 'custom_data', {})
    mod_cust_config = {}
    for k,f in config_data.items():

        # Check that we have a dictionary
        if type(f) != dict:
            log.debug("config.custom_data row was not a dictionary: {}".format(k))
            continue
        c_id = f.get('id', k)

        # Data supplied in with config (eg. from a multiqc_config.yaml file in working directory)
        if 'data' in f:
            try:
                cust_mods[c_id]['data'].update( f['data'] )
            except ValueError:
                # HTML plot type doesn't have a data sample-id key, so just take the whole chunk of data
                cust_mods[c_id]['data'] = f['data']
            cust_mods[c_id]['config'].update( { k:v for k, v in f.items() if k is not 'data' } )
            cust_mods[c_id]['config']['id'] = cust_mods[c_id]['config'].get('id', c_id)
            continue

        # Custom Content ID has search patterns in the config
        if c_id in report.files:
            cust_mods[c_id]['config'] = f
            cust_mods[c_id]['config']['id'] = cust_mods[c_id]['config'].get('id', c_id)
            search_patterns.append(c_id)
            continue

        # Must just be configuration for a separate custom-content class
        mod_cust_config[c_id] = f

    # Now go through each of the file search patterns
    bm = BaseMultiqcModule()
    for k in search_patterns:
        num_sp_found_files = 0
        for f in bm.find_log_files(k):
            num_sp_found_files += 1
            # Handle any exception without messing up for remaining custom content files
            try:
                f_extension = os.path.splitext(f['fn'])[1]

                # YAML and JSON files are the easiest
                parsed_data = None
                if f_extension == '.yaml' or f_extension == '.yml':
                    try:
                        parsed_data = yaml_ordered_load(f['f'])
                    except Exception as e:
                        log.warning("Error parsing YAML file '{}' (probably invalid YAML)".format(f['fn']))
                        log.debug("YAML error: {}".format(e), exc_info=True)
                        break
                elif f_extension == '.json':
                    try:
                        # Use OrderedDict for objects so that column order is honoured
                        parsed_data = json.loads(f['f'], object_pairs_hook=OrderedDict)
                    except Exception as e:
                        log.warning("Error parsing JSON file '{}' (probably invalid JSON)".format(f['fn']))
                        log.warning("JSON error: {}".format(e))
                        break
                elif f_extension == '.png' or f_extension == '.jpeg' or f_extension == '.jpg':
                    image_string = base64.b64encode(f['f'].read()).decode('utf-8')
                    image_format = 'png' if f_extension == '.png' else 'jpg'
                    img_html = '<div class="mqc-custom-content-image"><img src="data:image/{};base64,{}" /></div>'.format(image_format, image_string)
                    parsed_data = {
                        'id': f['s_name'],
                        'plot_type': 'image',
                        'section_name': f['s_name'].replace('_', ' ').replace('-', ' ').replace('.', ' '),
                        'data': img_html
                    }
                elif f_extension == '.html':
                    parsed_data = {
                        'id': f['s_name'],
                        'plot_type': 'html',
                        'data': f['f']
                    }
                    parsed_data.update( _find_html_file_header(f) )
                if parsed_data is not None:
                    c_id = parsed_data.get('id', k)
                    if len(parsed_data.get('data', {})) > 0:
                        if type(parsed_data['data']) == str:
                            cust_mods[c_id]['data'] = parsed_data['data']
                        else:
                            cust_mods[c_id]['data'].update( parsed_data['data'] )
                        cust_mods[c_id]['config'].update ( { j:k for j,k in parsed_data.items() if j != 'data' } )
                    else:
                        log.warning("No data found in {}".format(f['fn']))

                # txt, csv, tsv etc
                else:
                    # Look for configuration details in the header
                    m_config = _find_file_header( f )
                    s_name = None
                    if m_config is not None:
                        c_id = m_config.get('id', k)
                        # Update the base config with anything parsed from the file
                        b_config = cust_mods.get(c_id, {}).get('config', {})
                        b_config.update( m_config )
                        # Now set the module config to the merged dict
                        m_config = dict(b_config)
                        s_name = m_config.get('sample_name')
                    else:
                        c_id = k
                        m_config = cust_mods.get(c_id, {}).get('config', {})

                    # Guess sample name if not given
                    if s_name is None:
                        s_name = bm.clean_s_name(f['s_name'], f['root'])

                    # Guess c_id if no information known
                    if k == 'custom_content':
                        c_id = s_name

                    # Merge with config from a MultiQC config file if we have it
                    m_config.update(mod_cust_config.get(c_id, {}))

                    # Add information about the file to the config dict
                    if 'files' not in m_config:
                        m_config['files'] = dict()
                    m_config['files'].update( { s_name : { 'fn': f['fn'], 'root': f['root'] } } )

                    # Guess file format if not given
                    if m_config.get('file_format') is None:
                        m_config['file_format'] = _guess_file_format( f )
                    # Parse data
                    try:
                        parsed_data, conf = _parse_txt( f, m_config )
                        if parsed_data is None or len(parsed_data) == 0:
                            log.warning("Not able to parse custom data in {}".format(f['fn']))
                        else:
                            # Did we get a new section id from the file?
                            if conf.get('id') is not None:
                                c_id = conf.get('id')
                            # heatmap - special data type
                            if type(parsed_data) == list:
                                cust_mods[c_id]['data'] = parsed_data
                            elif conf.get('plot_type') == 'html':
                                cust_mods[c_id]['data'] = parsed_data
                            else:
                                cust_mods[c_id]['data'].update(parsed_data)
                            cust_mods[c_id]['config'].update(conf)
                    except (IndexError, AttributeError, TypeError):
                        log.error("Unexpected parsing error for {}".format(f['fn']), exc_info=True)
                        raise # testing
            except Exception as e:
                log.error("Uncaught exception raised for file '{}'".format(f['fn']))
                log.exception(e)

        # Give log message if no files found for search pattern
        if num_sp_found_files == 0 and k != 'custom_content':
            log.debug("No samples found: custom content ({})".format(k))

    # Filter to strip out ignored sample names
    for k in cust_mods:
        cust_mods[k]['data'] = bm.ignore_samples(cust_mods[k]['data'])

    # Remove any configs that have no data
    remove_cids = [ k for k in cust_mods if len(cust_mods[k]['data']) == 0 ]
    for k in remove_cids:
        del cust_mods[k]

    if len(cust_mods) == 0:
        raise UserWarning

    # Go through each data type
    parsed_modules = OrderedDict()
    for c_id, mod in cust_mods.items():

        # General Stats
        if mod['config'].get('plot_type') == 'generalstats':
            gsheaders = mod['config'].get('pconfig')
            if gsheaders is None:
                headers = set()
                for d in mod['data'].values():
                    headers.update(d.keys())
                headers = list(headers)
                headers.sort()
                gsheaders = OrderedDict()
                for h in headers:
                    gsheaders[h] = dict()

            # Headers is a list of dicts
            if type(gsheaders) == list:
                gsheaders_dict = OrderedDict()
                for gsheader in gsheaders:
                    for col_id, col_data in gsheader.items():
                        gsheaders_dict[col_id] = col_data
                gsheaders = gsheaders_dict

            # Add namespace and description if not specified
            for m_id in gsheaders:
                if 'namespace' not in gsheaders[m_id]:
                    gsheaders[m_id]['namespace'] = mod['config'].get('namespace', c_id)

            bm.general_stats_addcols(mod['data'], gsheaders)

        # Initialise this new module class and append to list
        else:
            # Is this file asking to be a sub-section under a parent section?
            mod_id = mod['config'].get('parent_id', c_id)
            # If we have any custom configuration from a MultiQC config file, update here
            # This is done earlier for tsv files too, but we do it here so that it overwrites what was in the file
            if mod_id in mod_cust_config:
                mod['config'].update(mod_cust_config[mod_id])
            # We've not seen this module section before (normal for most custom content)
            if mod_id not in parsed_modules:
                parsed_modules[mod_id] = MultiqcModule(mod_id, mod)
            else:
                # New sub-section
                parsed_modules[mod_id].update_init(c_id, mod)
            parsed_modules[mod_id].add_cc_section(c_id, mod)
            if mod['config'].get('plot_type') == 'html':
                log.info("{}: Found 1 sample (html)".format(c_id))
            elif mod['config'].get('plot_type') == 'image':
                log.info("{}: Found 1 sample (image)".format(c_id))
            else:
                log.info("{}: Found {} samples ({})".format(c_id, len(mod['data']), mod['config'].get('plot_type')))

    # Sort sections if we have a config option for order
    mod_order = getattr(config, 'custom_content', {}).get('order', [])
    sorted_modules = [parsed_mod for parsed_mod in parsed_modules.values() if parsed_mod.anchor not in mod_order ]
    sorted_modules.extend([parsed_mod for mod_id in mod_order for parsed_mod in parsed_modules.values() if parsed_mod.anchor == mod_id ])

    # If we only have General Stats columns then there are no module outputs
    if len(sorted_modules) == 0:
        raise UserWarning

    return sorted_modules