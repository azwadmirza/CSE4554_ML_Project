def tumbler_taker_finished_update(taker, schedulefile, tumble_log, options,
                   res, fromtx=False, waittime=0.0, txdetails=None):
    """on_finished_callback processing for tumbler.
    Note that this is *not* the full callback, but provides common
    processing across command line and other GUI versions.
    """

    if fromtx == "unconfirmed":
        #unconfirmed event means transaction has been propagated,
        #we update state to prevent accidentally re-creating it in
        #any crash/restart condition
        unconf_update(taker, schedulefile, tumble_log, True)
        return

    if fromtx:
        if res:
            #this has no effect except in the rare case that confirmation
            #is immediate; also it does not repeat the log entry.
            unconf_update(taker, schedulefile, tumble_log, False)
            #note that Qt does not yet support 'addrask', so this is only
            #for command line script TODO
            if taker.schedule[taker.schedule_index+1][3] == 'addrask':
                jm_single().debug_silence[0] = True
                print('\n'.join(['=' * 60] * 3))
                print('Tumbler requires more addresses to stop amount correlation')
                print('Obtain a new destination address from your bitcoin recipient')
                print(' for example click the button that gives a new deposit address')
                print('\n'.join(['=' * 60] * 1))
                while True:
                    destaddr = raw_input('insert new address: ')
                    addr_valid, errormsg = validate_address(destaddr)
                    if addr_valid:
                        break
                    print(
                    'Address ' + destaddr + ' invalid. ' + errormsg + ' try again')
                jm_single().debug_silence[0] = False
                taker.schedule[taker.schedule_index+1][3] = destaddr
                taker.tdestaddrs.append(destaddr)

            waiting_message = "Waiting for: " + str(waittime) + " minutes."
            tumble_log.info(waiting_message)
            log.info(waiting_message)
            txd, txid = txdetails
            taker.wallet.remove_old_utxos(txd)
            taker.wallet.add_new_utxos(txd, txid)
        else:
            #a transaction failed, either because insufficient makers
            #(acording to minimum_makers) responded in Phase 1, or not all
            #makers responded in Phase 2. We'll first try to repeat without the
            #troublemakers.
            log.info("Schedule entry: " + str(
                taker.schedule[taker.schedule_index]) + \
                     " failed after timeout, trying again")
            taker.add_ignored_makers(taker.nonrespondants)
            #Is the failure in Phase 2?
            if not taker.latest_tx is None:
                #Now we have to set the specific group we want to use, and hopefully
                #they will respond again as they showed honesty last time.
                #Note that we must wipe the list first; other honest makers needn't
                #have the right settings (e.g. max cjamount), so can't be carried
                #over from earlier transactions.
                taker.honest_makers = []
                taker.add_honest_makers(list(set(
                    taker.maker_utxo_data.keys()).symmetric_difference(
                        set(taker.nonrespondants))))
                #If insufficient makers were honest, we can only tweak the schedule.
                #If enough were, we prefer the restart with them only:
                log.info("Inside a Phase 2 failure; number of honest respondants was: " + str(len(taker.honest_makers)))
                log.info("They were: " + str(taker.honest_makers))
                if len(taker.honest_makers) >= jm_single().config.getint(
                    "POLICY", "minimum_makers"):
                    tumble_log.info("Transaction attempt failed, attempting to "
                                    "restart with subset.")
                    tumble_log.info("The paramaters of the failed attempt: ")
                    tumble_log.info(str(taker.schedule[taker.schedule_index]))
                    #we must reset the number of counterparties, as well as fix who they
                    #are; this is because the number is used to e.g. calculate fees.
                    #cleanest way is to reset the number in the schedule before restart.
                    taker.schedule[taker.schedule_index][2] = len(taker.honest_makers)
                    retry_str = "Retrying with: " + str(taker.schedule[
                        taker.schedule_index][2]) + " counterparties."
                    tumble_log.info(retry_str)
                    log.info(retry_str)
                    taker.set_honest_only(True)
                    taker.schedule_index -= 1
                    return

            #There were not enough honest counterparties.
            #Tumbler is aggressive in trying to complete; we tweak the schedule
            #from this point in the mixdepth, then try again.
            tumble_log.info("Transaction attempt failed, tweaking schedule"
                            " and trying again.")
            tumble_log.info("The paramaters of the failed attempt: ")
            tumble_log.info(str(taker.schedule[taker.schedule_index]))
            taker.schedule_index -= 1
            taker.schedule = tweak_tumble_schedule(options, taker.schedule,
                                                   taker.schedule_index,
                                                   taker.tdestaddrs)
            tumble_log.info("We tweaked the schedule, the new schedule is:")
            tumble_log.info(pprint.pformat(taker.schedule))
    else:
        if not res:
            failure_msg = "Did not complete successfully, shutting down"
            tumble_log.info(failure_msg)
            log.info(failure_msg)
        else:
            log.info("All transactions completed correctly")
            tumble_log.info("Completed successfully the last entry:")
            #Whether sweep or not, the amt is not in satoshis; use taker data
            hramt = taker.cjamount
            tumble_log.info(human_readable_schedule_entry(
                taker.schedule[taker.schedule_index], hramt))
            #copy of above, TODO refactor out
            taker.schedule[taker.schedule_index][5] = 1
            with open(schedulefile, "wb") as f:
                f.write(schedule_to_text(taker.schedule))