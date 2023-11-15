    def create_from_dists(cls, index, target_prefix, unlink_dists, link_dists):
        # This constructor method helps to patch into the 'plan' framework
        linked_packages_data_to_unlink = tuple(load_meta(target_prefix, dist)
                                               for dist in unlink_dists)

        log.debug("instantiating UnlinkLinkTransaction with\n"
                  "  target_prefix: %s\n"
                  "  unlink_dists:\n"
                  "    %s\n"
                  "  link_dists:\n"
                  "    %s\n",
                  target_prefix,
                  '\n    '.join(text_type(d) for d in unlink_dists),
                  '\n    '.join(text_type(d) for d in link_dists))

        pkg_dirs_to_link = tuple(PackageCache.get_entry_to_link(dist).extracted_package_dir
                                 for dist in link_dists)
        assert all(pkg_dirs_to_link)
        packages_info_to_link = tuple(read_package_info(index[dist], pkg_dir)
                                      for dist, pkg_dir in zip(link_dists, pkg_dirs_to_link))

        return UnlinkLinkTransaction(target_prefix, linked_packages_data_to_unlink,
                                     packages_info_to_link)