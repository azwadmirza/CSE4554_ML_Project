def uninstall(parser, args):
    if not args.packages and not args.all:
        tty.die("uninstall requires at least one package argument.")

    with spack.installed_db.write_transaction():

        uninstall_list = get_uninstall_list(args)

        if not args.yes_to_all:
            tty.msg("The following packages will be uninstalled : ")
            print('')
            spack.cmd.display_specs(uninstall_list, **display_args)
            print('')
            spack.cmd.ask_for_confirmation('Do you want to proceed ? ')

        # Uninstall everything on the list
        do_uninstall(uninstall_list, args.force)