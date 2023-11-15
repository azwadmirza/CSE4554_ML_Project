    def _link_folders(src, dst, linked_folders):
        for linked_folder in linked_folders:
            link = os.readlink(os.path.join(src, linked_folder))
            dst_link = os.path.join(dst, linked_folder)
            try:
                # Remove the previous symlink
                os.remove(dst_link)
            except OSError:
                pass
            # link is a string relative to linked_folder
            # e.j: os.symlink("test/bar", "./foo/test_link") will create a link to foo/test/bar in ./foo/test_link
            mkdir(os.path.dirname(dst_link))
            os.symlink(link, dst_link)
        # Remove empty links
        for linked_folder in linked_folders:
            dst_link = os.path.join(dst, linked_folder)
            abs_path = os.path.realpath(dst_link)
            if not os.path.exists(abs_path):
                os.remove(dst_link)