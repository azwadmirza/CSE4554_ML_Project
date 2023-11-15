    def create_file_link_actions(cls, transaction_context, package_info, target_prefix,
                                 requested_link_type):
        def get_prefix_replace(source_path_data):
            if source_path_data.path_type == PathType.softlink:
                link_type = LinkType.copy
                prefix_placehoder, file_mode = '', None
            elif source_path_data.prefix_placeholder:
                link_type = LinkType.copy
                prefix_placehoder = source_path_data.prefix_placeholder
                file_mode = source_path_data.file_mode
            elif source_path_data.no_link:
                link_type = LinkType.copy
                prefix_placehoder, file_mode = '', None
            else:
                link_type = requested_link_type
                prefix_placehoder, file_mode = '', None

            return link_type, prefix_placehoder, file_mode

        def make_file_link_action(source_path_data):
            # TODO: this inner function is still kind of a mess
            noarch = package_info.repodata_record.noarch
            if noarch == NoarchType.python:
                sp_dir = transaction_context['target_site_packages_short_path']
                if sp_dir is None:
                    raise CondaError("Unable to determine python site-packages "
                                     "dir in target_prefix!\nPlease make sure "
                                     "python is installed in %s" % target_prefix)
                target_short_path = get_python_noarch_target_path(source_path_data.path, sp_dir)
            elif noarch is None or noarch == NoarchType.generic:
                target_short_path = source_path_data.path
            else:
                raise CondaUpgradeError(dals("""
                The current version of conda is too old to install this package.
                Please update conda."""))

            link_type, placeholder, fmode = get_prefix_replace(source_path_data)

            if placeholder:
                return PrefixReplaceLinkAction(transaction_context, package_info,
                                               package_info.extracted_package_dir,
                                               source_path_data.path,
                                               target_prefix, target_short_path,
                                               requested_link_type,
                                               placeholder, fmode, source_path_data)
            else:
                return LinkPathAction(transaction_context, package_info,
                                      package_info.extracted_package_dir, source_path_data.path,
                                      target_prefix, target_short_path,
                                      link_type, source_path_data)
        return tuple(make_file_link_action(spi) for spi in package_info.paths_data.paths)