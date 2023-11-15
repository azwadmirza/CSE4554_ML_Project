def _edit_search_results(config, journal, old_entries, **kwargs):
    """
    1. Send the given journal entries to the user-configured editor
    2. Print out stats on any modifications to journal
    3. Write modifications to journal
    """
    if not config["editor"]:
        print(
            f"""
            [{ERROR_COLOR}ERROR{RESET_COLOR}: There is no editor configured.]

            Please specify an editor in config file ({install.CONFIG_FILE_PATH})
            to use the --edit option.
            """,
            file=sys.stderr,
        )
        sys.exit(1)

    # separate entries we are not editing
    other_entries = [e for e in old_entries if e not in journal.entries]

    # Get stats now for summary later
    old_stats = _get_predit_stats(journal)

    # Send user to the editor
    edited = get_text_from_editor(config, journal.editable_str())
    journal.parse_editable_str(edited)

    # Print summary if available
    _print_edited_summary(journal, old_stats)

    # Put back entries we separated earlier, sort, and write the journal
    journal.entries += other_entries
    journal.sort()
    journal.write()