def menu_download_from_online_image_bookmark(opisvalid, args):
    __log__.info("User's Image Bookmark mode.")
    start_page = 1
    end_page = 0
    hide = 'n'
    tag = ''
    sorting = 'desc'

    if opisvalid and len(args) > 0:
        hide = args[0].lower()
        if hide not in ('y', 'n', 'o'):
            print("Invalid args: ", args)
            return
        (start_page, end_page) = get_start_and_end_number_from_args(args, offset=1)
        if len(args) > 3:
            tag = args[3]
        if len(args) > 4:
            sorting = args[4].lower()
            if sorting not in ('asc', 'desc', 'date', 'date_d'):
                print("Invalid sorting order: ", sorting)
                return
    else:
        hide = input("Include Private bookmarks [y/n/o]: ").rstrip("\r") or 'n'
        hide = hide.lower()
        if hide not in ('y', 'n', 'o'):
            print("Invalid args: ", hide)
            return
        tag = input("Tag (default=All Images): ").rstrip("\r") or ''
        (start_page, end_page) = get_start_and_end_number()
        # sorting = input("Sort Order [asc/desc/date/date_d]: ").rstrip("\r") or 'desc'
        # sorting = sorting.lower()
        # if sorting not in ('asc', 'desc', 'date', 'date_d'):
        #     print("Invalid sorting order: ", sorting)
        #     return

    process_image_bookmark(hide, start_page, end_page, tag, sorting)