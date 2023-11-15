        def make_file_link_action(source_path_data):
            # TODO: this inner function is still kind of a mess
            noarch = package_info.repodata_record.noarch
            if noarch == NoarchType.python:
                sp_dir = transaction_context['target_site_packages_short_path']
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