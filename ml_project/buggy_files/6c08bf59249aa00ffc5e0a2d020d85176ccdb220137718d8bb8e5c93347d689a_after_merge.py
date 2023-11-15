def wallet_tool_main(wallet_root_path):
    """Main wallet tool script function; returned is a string (output or error)
    """
    parser = get_wallettool_parser()
    (options, args) = parser.parse_args()
    load_program_config(config_path=options.datadir)
    check_regtest(blockchain_start=False)
    # full path to the wallets/ subdirectory in the user data area:
    wallet_root_path = os.path.join(jm_single().datadir, wallet_root_path)
    noseed_methods = ['generate', 'recover', 'createwatchonly']
    methods = ['display', 'displayall', 'summary', 'showseed', 'importprivkey',
               'history', 'showutxos', 'freeze', 'gettimelockaddress',
               'addtxoutproof', 'changepass']
    methods.extend(noseed_methods)
    noscan_methods = ['showseed', 'importprivkey', 'dumpprivkey', 'signmessage',
                      'changepass']
    readonly_methods = ['display', 'displayall', 'summary', 'showseed',
                        'history', 'showutxos', 'dumpprivkey', 'signmessage',
                        'gettimelockaddress']

    if len(args) < 1:
        parser.error('Needs a wallet file or method')
        sys.exit(EXIT_ARGERROR)

    if options.mixdepth is not None and options.mixdepth < 0:
        parser.error("Must have at least one mixdepth.")
        sys.exit(EXIT_ARGERROR)

    if args[0] in noseed_methods:
        method = args[0]
        if options.mixdepth is None:
            options.mixdepth = DEFAULT_MIXDEPTH
    else:
        seed = args[0]
        wallet_path = get_wallet_path(seed, wallet_root_path)
        method = ('display' if len(args) == 1 else args[1].lower())
        read_only = method in readonly_methods

        #special case needed for fidelity bond burner outputs
        #maybe theres a better way to do this
        if options.recoversync:
            read_only = False

        wallet = open_test_wallet_maybe(
            wallet_path, seed, options.mixdepth, read_only=read_only,
            wallet_password_stdin=options.wallet_password_stdin, gap_limit=options.gaplimit)

        # this object is only to respect the layering,
        # the service will not be started since this is a synchronous script:
        wallet_service = WalletService(wallet)
        if wallet_service.rpc_error:
            sys.exit(EXIT_FAILURE)

        if method not in noscan_methods and jm_single().bc_interface is not None:
            # if nothing was configured, we override bitcoind's options so that
            # unconfirmed balance is included in the wallet display by default
            if 'listunspent_args' not in jm_single().config.options('POLICY'):
                jm_single().config.set('POLICY','listunspent_args', '[0]')
            while True:
                if wallet_service.sync_wallet(fast = not options.recoversync):
                    break

    #Now the wallet/data is prepared, execute the script according to the method
    if method == "display":
        return wallet_display(wallet_service, options.showprivkey)
    elif method == "displayall":
        return wallet_display(wallet_service, options.showprivkey,
                              displayall=True)
    elif method == "summary":
        return wallet_display(wallet_service, options.showprivkey, summarized=True)
    elif method == "history":
        if not isinstance(jm_single().bc_interface, BitcoinCoreInterface):
            jmprint('showing history only available when using the Bitcoin Core ' +
                    'blockchain interface', "error")
            sys.exit(EXIT_ARGERROR)
        else:
            return wallet_fetch_history(wallet_service, options)
    elif method == "generate":
        retval = wallet_generate_recover("generate", wallet_root_path,
                                         mixdepth=options.mixdepth)
        return "Generated wallet OK" if retval else "Failed"
    elif method == "recover":
        retval = wallet_generate_recover("recover", wallet_root_path,
                                         mixdepth=options.mixdepth)
        return "Recovered wallet OK" if retval else "Failed"
    elif method == "changepass":
        retval = wallet_change_passphrase(wallet_service)
        return "Changed encryption passphrase OK" if retval else "Failed"
    elif method == "showutxos":
        return wallet_showutxos(wallet_service, options.showprivkey)
    elif method == "showseed":
        return wallet_showseed(wallet_service)
    elif method == "dumpprivkey":
        return wallet_dumpprivkey(wallet_service, options.hd_path)
    elif method == "importprivkey":
        #note: must be interactive (security)
        if options.mixdepth is None:
            parser.error("You need to specify a mixdepth with -m")
        wallet_importprivkey(wallet_service, options.mixdepth,
                             map_key_type(options.key_type))
        return "Key import completed."
    elif method == "signmessage":
        if len(args) < 3:
            jmprint('Must provide message to sign', "error")
            sys.exit(EXIT_ARGERROR)
        return wallet_signmessage(wallet_service, options.hd_path, args[2])
    elif method == "freeze":
        return wallet_freezeutxo(wallet_service, options.mixdepth)
    elif method == "gettimelockaddress":
        if len(args) < 3:
            jmprint('Must have locktime value yyyy-mm. For example 2021-03', "error")
            sys.exit(EXIT_ARGERROR)
        return wallet_gettimelockaddress(wallet_service.wallet, args[2])
    elif method == "addtxoutproof":
        if len(args) < 3:
            jmprint('Must have txout proof, which is the output of Bitcoin '
                + 'Core\'s RPC call gettxoutproof', "error")
            sys.exit(EXIT_ARGERROR)
        return wallet_addtxoutproof(wallet_service, options.hd_path, args[2])
    elif method == "createwatchonly":
        if len(args) < 2:
            jmprint("args: [master public key]", "error")
            sys.exit(EXIT_ARGERROR)
        return wallet_createwatchonly(wallet_root_path, args[1])
    else:
        parser.error("Unknown wallet-tool method: " + method)
        sys.exit(EXIT_ARGERROR)