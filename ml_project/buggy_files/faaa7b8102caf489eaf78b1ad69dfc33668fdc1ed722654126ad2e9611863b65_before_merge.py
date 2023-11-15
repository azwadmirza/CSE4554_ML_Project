def do_export_realm(realm: Realm, output_dir: Path, threads: int,
                    exportable_user_ids: Optional[Set[int]]=None) -> None:
    response = {}  # type: TableData

    # We need at least one thread running to export
    # UserMessage rows.  The management command should
    # enforce this for us.
    if not settings.TEST_SUITE:
        assert threads >= 1

    assert os.path.exists("./manage.py")

    realm_config = get_realm_config()

    create_soft_link(source=output_dir, in_progress=True)

    logging.info("Exporting data from get_realm_config()...")
    export_from_config(
        response=response,
        config=realm_config,
        seed_object=realm,
        context=dict(realm=realm, exportable_user_ids=exportable_user_ids)
    )
    logging.info('...DONE with get_realm_config() data')

    sanity_check_output(response)

    logging.info("Exporting uploaded files and avatars")
    export_uploads_and_avatars(realm, output_dir)

    # We (sort of) export zerver_message rows here.  We write
    # them to .partial files that are subsequently fleshed out
    # by parallel processes to add in zerver_usermessage data.
    # This is for performance reasons, of course.  Some installations
    # have millions of messages.
    logging.info("Exporting .partial files messages")
    message_ids = export_partial_message_files(realm, response, output_dir=output_dir)
    logging.info('%d messages were exported' % (len(message_ids)))

    # zerver_reaction
    zerver_reaction = {}  # type: TableData
    fetch_reaction_data(response=zerver_reaction, message_ids=message_ids)
    response.update(zerver_reaction)

    # Write realm data
    export_file = os.path.join(output_dir, "realm.json")
    write_data_to_file(output_file=export_file, data=response)
    logging.info('Writing realm data to %s' % (export_file,))

    # zerver_attachment
    export_attachment_table(realm=realm, output_dir=output_dir, message_ids=message_ids)

    # Start parallel jobs to export the UserMessage objects.
    launch_user_message_subprocesses(threads=threads, output_dir=output_dir)

    logging.info("Finished exporting %s" % (realm.string_id))
    create_soft_link(source=output_dir, in_progress=False)