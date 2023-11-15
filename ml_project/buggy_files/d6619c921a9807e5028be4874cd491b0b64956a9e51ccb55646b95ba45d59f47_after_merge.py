def _prompt_issue(recent_command_list):
    if recent_command_list:
        max_idx = len(recent_command_list) - 1
        ans = -1
        help_string = 'Please choose between 0 and {}, or enter q to quit: '.format(max_idx)

        while ans < 0 or ans > max_idx:
            try:
                ans = prompt(_MSG_CMD_ISSUE.format(max_idx), help_string=help_string)
                if ans.lower() in ["q", "quit"]:
                    ans = ans.lower()
                    break
                ans = int(ans)
            except ValueError:
                logger.warning(help_string)
                ans = -1

    else:
        ans = None
        help_string = 'Please choose between Y and N: '

        while not ans:
            ans = prompt(_MSG_ISSUE, help_string=help_string)
            if ans.lower() not in ["y", "n", "yes", "no", "q"]:
                ans = None
                continue

            # strip to short form
            ans = ans[0].lower() if ans else None

    if ans in ["y", "n"]:
        if ans == "y":
            prefix, url, original_issue = _build_issue_info_tup()
        else:
            return False
    else:
        if ans in ["q", "quit"]:
            return False
        if ans == 0:
            prefix, url, original_issue = _build_issue_info_tup()
        else:
            prefix, url, original_issue = _build_issue_info_tup(recent_command_list[ans])
    print(prefix)

    logger.info(original_issue)
    # if we are not in cloud shell and can launch a browser, launch it with the issue draft
    if can_launch_browser() and not in_cloud_console():
        open_page_in_browser(url)
    else:
        print("There isn't an available browser to create an issue draft. You can copy and paste the url"
              " below in a browser to submit.\n\n{}\n\n".format(url))

    return True