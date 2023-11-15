def check_user_image_inline(user_id, image_id, tag, bundle):
    """
    Execute a policy evaluation using the info in the request body including the bundle content

    :param user_id:
    :param image_id:
    :param tag:
    :param bundle:
    :return:
    """

    timer = time.time()
    db = get_session()
    cache_mgr = None

    try:
        # Input validation
        if tag is None:
            # set tag value to a value that only matches wildcards
            tag = '*/*:*'

        try:
            img_obj = db.query(Image).get((image_id, user_id))
        except:
            abort(Response(response='Image not found', status=404))

        if not img_obj:
            log.info('Request for evaluation of image that cannot be found: user_id = {}, image_id = {}'.format(user_id, image_id))
            abort(Response(response='Image not found', status=404))

        if evaluation_cache_enabled:
            timer2 = time.time()
            try:
                try:
                    cache_mgr = EvaluationCacheManager(img_obj, tag, bundle)
                except ValueError as err:
                    log.warn('Could not leverage cache due to error in bundle data: {}'.format(err))
                    cache_mgr = None

                if cache_mgr is None:
                    log.info('Could not initialize cache manager for policy evaluation, skipping cache usage')
                else:
                    cached_result = cache_mgr.refresh()
                    if cached_result:
                        metrics.counter_inc(name='anchore_policy_evaluation_cache_hits')
                        metrics.histogram_observe('anchore_policy_evaluation_cache_access_latency', time.time() - timer2,
                                                  status="hit")
                        log.info('Returning cached result of policy evaluation for {}/{}, with tag {} and bundle {} with digest {}. Last evaluation: {}'.format(user_id, image_id, tag, cache_mgr.bundle_id, cache_mgr.bundle_digest, cached_result.get('last_modified')))
                        return cached_result
                    else:
                        metrics.counter_inc(name='anchore_policy_evaluation_cache_misses')
                        metrics.histogram_observe('anchore_policy_evaluation_cache_access_latency', time.time() - timer2,
                                                  status="miss")
                        log.info('Policy evaluation not cached, or invalid, executing evaluation for {}/{} with tag {} and bundle {} with digest {}'.format(user_id, image_id, tag, cache_mgr.bundle_id, cache_mgr.bundle_digest))

            except Exception as ex:
                log.exception('Unexpected error operating on policy evaluation cache. Skipping use of cache.')

        else:
            log.info('Policy evaluation cache disabled. Executing evaluation')

        # Build bundle exec.
        problems = []
        executable_bundle = None
        try:
            # Allow deprecated gates here to support upgrade cases from old policy bundles.
            executable_bundle = build_bundle(bundle, for_tag=tag, allow_deprecated=True)
            if executable_bundle.init_errors:
                problems = executable_bundle.init_errors
        except InitializationError as e:
            log.exception('Bundle construction and initialization returned errors')
            problems = e.causes

        eval_result = None
        if not problems:
            # Execute bundle
            try:
                eval_result = executable_bundle.execute(img_obj, tag, ExecutionContext(db_session=db, configuration={}))
            except Exception as e:
                log.exception('Error executing policy bundle {} against image {} w/tag {}: {}'.format(bundle['id'], image_id, tag, e.message))
                abort(Response(response='Cannot execute given policy against the image due to errors executing the policy bundle: {}'.format(e.message), status=500))
        else:
            # Construct a failure eval with details on the errors and mappings to send to client
            eval_result = build_empty_error_execution(img_obj, tag, executable_bundle, errors=problems, warnings=[])
            if executable_bundle and executable_bundle.mapping and len(executable_bundle.mapping.mapping_rules) == 1:
                eval_result.executed_mapping = executable_bundle.mapping.mapping_rules[0]

        resp = PolicyEvaluation()
        resp.user_id = user_id
        resp.image_id = image_id
        resp.tag = tag
        resp.bundle = bundle
        resp.matched_mapping_rule = eval_result.executed_mapping.json() if eval_result.executed_mapping else False
        resp.last_modified = int(time.time())
        resp.final_action = eval_result.bundle_decision.final_decision.name
        resp.final_action_reason = eval_result.bundle_decision.reason
        resp.matched_whitelisted_images_rule = eval_result.bundle_decision.whitelisted_image.json() if eval_result.bundle_decision.whitelisted_image else False
        resp.matched_blacklisted_images_rule = eval_result.bundle_decision.blacklisted_image.json() if eval_result.bundle_decision.blacklisted_image else False
        resp.result = eval_result.as_table_json()
        resp.created_at = int(time.time())
        resp.evaluation_problems = [problem_from_exception(i) for i in eval_result.errors]
        resp.evaluation_problems += [problem_from_exception(i) for i in eval_result.warnings]
        if resp.evaluation_problems:
            for i in resp.evaluation_problems:
                log.warn('Returning evaluation response for image {}/{} w/tag {} and bundle {} that contains error: {}'.format(user_id, image_id, tag, bundle['id'], json.dumps(i.to_dict())))
            metrics.histogram_observe('anchore_policy_evaluation_time_seconds', time.time() - timer, status="fail")
        else:
            metrics.histogram_observe('anchore_policy_evaluation_time_seconds', time.time() - timer, status="success")

        result = resp.to_dict()

        # Never let the cache block returning results
        try:
            if evaluation_cache_enabled and cache_mgr is not None:
                cache_mgr.save(result)
        except Exception as ex:
            log.exception("Failed saving policy result in cache. Skipping and continuing.")

        db.commit()

        return result

    except HTTPException as e:
        db.rollback()
        log.exception('Caught exception in execution: {}'.format(e))
        raise
    except Exception as e:
        db.rollback()
        log.exception('Failed processing bundle evaluation: {}'.format(e))
        abort(Response('Unexpected internal error', 500))
    finally:
        db.close()