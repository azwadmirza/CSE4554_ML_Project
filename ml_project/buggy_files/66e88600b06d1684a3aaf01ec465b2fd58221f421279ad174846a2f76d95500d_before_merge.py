def binary_analysis(src, tools_dir, app_dir, executable_name):
    """Binary Analysis of IPA."""
    try:
        binary_analysis_dict = {}
        logger.info('Starting Binary Analysis')
        dirs = os.listdir(src)
        dot_app_dir = ''
        for dir_ in dirs:
            if dir_.endswith('.app'):
                dot_app_dir = dir_
                break
        # Bin Dir - Dir/Payload/x.app/
        bin_dir = os.path.join(src, dot_app_dir)
        if executable_name is None:
            bin_name = dot_app_dir.replace('.app', '')
        else:
            bin_name = executable_name
        # Bin Path - Dir/Payload/x.app/x
        bin_path = os.path.join(bin_dir, bin_name)
        binary_analysis_dict['libs'] = []
        binary_analysis_dict['bin_res'] = []
        binary_analysis_dict['strings'] = []
        if not is_file_exists(bin_path):
            logger.warning('MobSF Cannot find binary in %s', bin_path)
            logger.warning('Skipping Otool, Classdump and Strings')
        else:
            bin_info = get_bin_info(bin_path)
            otool_dict = otool_analysis(tools_dir, bin_name, bin_path, bin_dir)
            bin_type = detect_bin_type(otool_dict['libs'])
            cls_dump = class_dump(tools_dir, bin_path, app_dir, bin_type)
            if not cls_dump:
                cls_dump = {}
            strings_in_ipa = strings_on_ipa(bin_path)
            otool_dict['anal'] = list(
                filter(None, otool_dict['anal'] + [cls_dump]))
            binary_analysis_dict['libs'] = otool_dict['libs']
            binary_analysis_dict['bin_res'] = otool_dict['anal']
            binary_analysis_dict['strings'] = strings_in_ipa
            binary_analysis_dict['macho'] = bin_info
            binary_analysis_dict['bin_type'] = bin_type

        return binary_analysis_dict
    except Exception:
        logger.exception('iOS Binary Analysis')