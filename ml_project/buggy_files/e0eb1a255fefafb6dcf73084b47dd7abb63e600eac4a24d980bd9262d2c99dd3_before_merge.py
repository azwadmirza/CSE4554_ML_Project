    def trace_dispatch(self, frame, event, arg):
    # ENDIF
        # Note: this is a big function because most of the logic related to hitting a breakpoint and
        # stepping is contained in it. Ideally this could be split among multiple functions, but the
        # problem in this case is that in pure-python function calls are expensive and even more so
        # when tracing is on (because each function call will get an additional tracing call). We
        # try to address this by using the info.is_tracing for the fastest possible return, but the
        # cost is still high (maybe we could use code-generation in the future and make the code
        # generation be better split among what each part does).

        # DEBUG = '_debugger_case_generator.py' in frame.f_code.co_filename
        main_debugger, filename, info, thread, frame_skips_cache, frame_cache_key = self._args
        # if DEBUG: print('frame trace_dispatch %s %s %s %s %s %s, stop: %s' % (frame.f_lineno, frame.f_code.co_name, frame.f_code.co_filename, event, constant_to_str(info.pydev_step_cmd), arg, info.pydev_step_stop))
        try:
            info.is_tracing += 1
            line = frame.f_lineno
            line_cache_key = (frame_cache_key, line)

            if main_debugger.pydb_disposed:
                return None if event == 'call' else NO_FTRACE

            plugin_manager = main_debugger.plugin
            has_exception_breakpoints = main_debugger.break_on_caught_exceptions or main_debugger.has_plugin_exception_breaks

            stop_frame = info.pydev_step_stop
            step_cmd = info.pydev_step_cmd

            if frame.f_code.co_flags & 0xa0:  # 0xa0 ==  CO_GENERATOR = 0x20 | CO_COROUTINE = 0x80
                # Dealing with coroutines and generators:
                # When in a coroutine we change the perceived event to the debugger because
                # a call, StopIteration exception and return are usually just pausing/unpausing it.
                if event == 'line':
                    is_line = True
                    is_call = False
                    is_return = False
                    is_exception_event = False

                elif event == 'return':
                    is_line = False
                    is_call = False
                    is_return = True
                    is_exception_event = False

                    returns_cache_key = (frame_cache_key, 'returns')
                    return_lines = frame_skips_cache.get(returns_cache_key)
                    if return_lines is None:
                        # Note: we're collecting the return lines by inspecting the bytecode as
                        # there are multiple returns and multiple stop iterations when awaiting and
                        # it doesn't give any clear indication when a coroutine or generator is
                        # finishing or just pausing.
                        return_lines = set()
                        for x in main_debugger.collect_return_info(frame.f_code):
                            # Note: cython does not support closures in cpdefs (so we can't use
                            # a list comprehension).
                            return_lines.add(x.return_line)

                        frame_skips_cache[returns_cache_key] = return_lines

                    if line not in return_lines:
                        # Not really a return (coroutine/generator paused).
                        return self.trace_dispatch
                    else:
                        # Tricky handling: usually when we're on a frame which is about to exit
                        # we set the step mode to step into, but in this case we'd end up in the
                        # asyncio internal machinery, which is not what we want, so, we just
                        # ask the stop frame to be a level up.
                        #
                        # Note that there's an issue here which we may want to fix in the future: if
                        # the back frame is a frame which is filtered, we won't stop properly.
                        # Solving this may not be trivial as we'd need to put a scope in the step
                        # in, but we may have to do it anyways to have a step in which doesn't end
                        # up in asyncio).
                        if stop_frame is frame:
                            if step_cmd in (CMD_STEP_OVER, CMD_STEP_OVER_MY_CODE, CMD_STEP_INTO, CMD_STEP_INTO_MY_CODE):
                                f = self._get_unfiltered_back_frame(main_debugger, frame)
                                if f is not None:
                                    info.pydev_step_cmd = CMD_STEP_INTO_COROUTINE
                                    info.pydev_step_stop = f
                                else:
                                    if step_cmd == CMD_STEP_OVER:
                                        info.pydev_step_cmd = CMD_STEP_INTO
                                        info.pydev_step_stop = None

                                    elif step_cmd == CMD_STEP_OVER_MY_CODE:
                                        info.pydev_step_cmd = CMD_STEP_INTO_MY_CODE
                                        info.pydev_step_stop = None

                            elif step_cmd == CMD_STEP_INTO_COROUTINE:
                                # We're exiting this one, so, mark the new coroutine context.
                                f = self._get_unfiltered_back_frame(main_debugger, frame)
                                if f is not None:
                                    info.pydev_step_stop = f
                                else:
                                    info.pydev_step_cmd = CMD_STEP_INTO
                                    info.pydev_step_stop = None

                elif event == 'exception':
                    breakpoints_for_file = None
                    if has_exception_breakpoints:
                        should_stop, frame = self.should_stop_on_exception(frame, event, arg)
                        if should_stop:
                            self.handle_exception(frame, event, arg)
                            return self.trace_dispatch

                    return self.trace_dispatch
                else:
                    # event == 'call' or event == 'c_XXX'
                    return self.trace_dispatch

            else:
                if event == 'line':
                    is_line = True
                    is_call = False
                    is_return = False
                    is_exception_event = False

                elif event == 'return':
                    is_line = False
                    is_return = True
                    is_call = False
                    is_exception_event = False

                    # If we are in single step mode and something causes us to exit the current frame, we need to make sure we break
                    # eventually.  Force the step mode to step into and the step stop frame to None.
                    # I.e.: F6 in the end of a function should stop in the next possible position (instead of forcing the user
                    # to make a step in or step over at that location).
                    # Note: this is especially troublesome when we're skipping code with the
                    # @DontTrace comment.
                    if stop_frame is frame and is_return and step_cmd in (CMD_STEP_OVER, CMD_STEP_RETURN, CMD_STEP_OVER_MY_CODE, CMD_STEP_RETURN_MY_CODE):
                        if step_cmd in (CMD_STEP_OVER, CMD_STEP_RETURN):
                            info.pydev_step_cmd = CMD_STEP_INTO
                        else:
                            info.pydev_step_cmd = CMD_STEP_INTO_MY_CODE
                        info.pydev_step_stop = None

                elif event == 'call':
                    is_line = False
                    is_call = True
                    is_return = False
                    is_exception_event = False

                elif event == 'exception':
                    is_exception_event = True
                    breakpoints_for_file = None
                    if has_exception_breakpoints:
                        should_stop, frame = self.should_stop_on_exception(frame, event, arg)
                        if should_stop:
                            self.handle_exception(frame, event, arg)
                            return self.trace_dispatch
                    is_line = False
                    is_return = False
                    is_call = False

                else:
                    # Unexpected: just keep the same trace func (i.e.: event == 'c_XXX').
                    return self.trace_dispatch

            if not is_exception_event:
                breakpoints_for_file = main_debugger.breakpoints.get(filename)

                can_skip = False

                if info.pydev_state == 1:  # STATE_RUN = 1
                    # we can skip if:
                    # - we have no stop marked
                    # - we should make a step return/step over and we're not in the current frame
                    # - we're stepping into a coroutine context and we're not in that context
                    if step_cmd == -1:
                        can_skip = True

                    elif step_cmd in (CMD_STEP_OVER, CMD_STEP_RETURN, CMD_STEP_OVER_MY_CODE, CMD_STEP_RETURN_MY_CODE) and stop_frame is not frame:
                        can_skip = True

                    elif step_cmd == CMD_STEP_INTO_COROUTINE:
                        f = frame
                        while f is not None:
                            if f is stop_frame:
                                break
                            f = f.f_back
                        else:
                            can_skip = True

                    if can_skip:
                        if plugin_manager is not None and (
                                main_debugger.has_plugin_line_breaks or main_debugger.has_plugin_exception_breaks):
                            can_skip = plugin_manager.can_skip(main_debugger, frame)

                        if can_skip and main_debugger.show_return_values and info.pydev_step_cmd in (CMD_STEP_OVER, CMD_STEP_OVER_MY_CODE) and frame.f_back is stop_frame:
                            # trace function for showing return values after step over
                            can_skip = False

                # Let's check to see if we are in a function that has a breakpoint. If we don't have a breakpoint,
                # we will return nothing for the next trace
                # also, after we hit a breakpoint and go to some other debugging state, we have to force the set trace anyway,
                # so, that's why the additional checks are there.
                if not breakpoints_for_file:
                    if can_skip:
                        if has_exception_breakpoints:
                            return self.trace_exception
                        else:
                            return None if is_call else NO_FTRACE

                else:
                    # When cached, 0 means we don't have a breakpoint and 1 means we have.
                    if can_skip:
                        breakpoints_in_line_cache = frame_skips_cache.get(line_cache_key, -1)
                        if breakpoints_in_line_cache == 0:
                            return self.trace_dispatch

                    breakpoints_in_frame_cache = frame_skips_cache.get(frame_cache_key, -1)
                    if breakpoints_in_frame_cache != -1:
                        # Gotten from cache.
                        has_breakpoint_in_frame = breakpoints_in_frame_cache == 1

                    else:
                        has_breakpoint_in_frame = False

                        func_lines = _get_func_lines(frame.f_code)
                        if func_lines is None:
                            # This is a fallback for implementations where we can't get the function
                            # lines -- i.e.: jython (in this case clients need to provide the function
                            # name to decide on the skip or we won't be able to skip the function
                            # completely).

                            # Checks the breakpoint to see if there is a context match in some function.
                            curr_func_name = frame.f_code.co_name

                            # global context is set with an empty name
                            if curr_func_name in ('?', '<module>', '<lambda>'):
                                curr_func_name = ''

                            for bp in dict_iter_values(breakpoints_for_file):  # jython does not support itervalues()
                                # will match either global or some function
                                if bp.func_name in ('None', curr_func_name):
                                    has_breakpoint_in_frame = True
                                    break
                        else:
                            for bp_line in breakpoints_for_file:  # iterate on keys
                                if bp_line in func_lines:
                                    has_breakpoint_in_frame = True
                                    break

                        # Cache the value (1 or 0 or -1 for default because of cython).
                        if has_breakpoint_in_frame:
                            frame_skips_cache[frame_cache_key] = 1
                        else:
                            frame_skips_cache[frame_cache_key] = 0

                    if can_skip and not has_breakpoint_in_frame:
                        if has_exception_breakpoints:
                            return self.trace_exception
                        else:
                            return None if is_call else NO_FTRACE

            # We may have hit a breakpoint or we are already in step mode. Either way, let's check what we should do in this frame
            # if DEBUG: print('NOT skipped: %s %s %s %s' % (frame.f_lineno, frame.f_code.co_name, event, frame.__class__.__name__))

            try:
                flag = False
                # return is not taken into account for breakpoint hit because we'd have a double-hit in this case
                # (one for the line and the other for the return).

                stop_info = {}
                breakpoint = None
                exist_result = False
                stop = False
                bp_type = None
                if not is_return and info.pydev_state != STATE_SUSPEND and breakpoints_for_file is not None and line in breakpoints_for_file:
                    breakpoint = breakpoints_for_file[line]
                    new_frame = frame
                    stop = True
                    if step_cmd in (CMD_STEP_OVER, CMD_STEP_OVER_MY_CODE) and (stop_frame is frame and is_line):
                        stop = False  # we don't stop on breakpoint if we have to stop by step-over (it will be processed later)
                elif plugin_manager is not None and main_debugger.has_plugin_line_breaks:
                    result = plugin_manager.get_breakpoint(main_debugger, self, frame, event, self._args)
                    if result:
                        exist_result = True
                        flag, breakpoint, new_frame, bp_type = result

                if breakpoint:
                    # ok, hit breakpoint, now, we have to discover if it is a conditional breakpoint
                    # lets do the conditional stuff here
                    if stop or exist_result:
                        eval_result = False
                        if breakpoint.has_condition:
                            eval_result = main_debugger.handle_breakpoint_condition(info, breakpoint, new_frame)

                        if breakpoint.expression is not None:
                            main_debugger.handle_breakpoint_expression(breakpoint, info, new_frame)
                            if breakpoint.is_logpoint and info.pydev_message is not None and len(info.pydev_message) > 0:
                                cmd = main_debugger.cmd_factory.make_io_message(info.pydev_message + os.linesep, '1')
                                main_debugger.writer.add_command(cmd)

                        if breakpoint.has_condition:
                            if not eval_result:
                                stop = False
                        elif breakpoint.is_logpoint:
                            stop = False

                    if is_call and frame.f_code.co_name in ('<module>', '<lambda>'):
                        # If we find a call for a module, it means that the module is being imported/executed for the
                        # first time. In this case we have to ignore this hit as it may later duplicated by a
                        # line event at the same place (so, if there's a module with a print() in the first line
                        # the user will hit that line twice, which is not what we want).
                        #
                        # As for lambda, as it only has a single statement, it's not interesting to trace
                        # its call and later its line event as they're usually in the same line.

                        return self.trace_dispatch

                if main_debugger.show_return_values:
                    if is_return and (
                            (info.pydev_step_cmd in (CMD_STEP_OVER, CMD_STEP_OVER_MY_CODE) and (frame.f_back is stop_frame)) or
                            (info.pydev_step_cmd in (CMD_STEP_RETURN, CMD_STEP_RETURN_MY_CODE) and (frame is stop_frame)) or
                            (info.pydev_step_cmd in (CMD_STEP_INTO, CMD_STEP_INTO_MY_CODE, CMD_STEP_INTO_COROUTINE))
                        ):
                        self.show_return_values(frame, arg)

                elif main_debugger.remove_return_values_flag:
                    try:
                        self.remove_return_values(main_debugger, frame)
                    finally:
                        main_debugger.remove_return_values_flag = False

                if stop:
                    self.set_suspend(
                        thread,
                        CMD_SET_BREAK,
                        suspend_other_threads=breakpoint and breakpoint.suspend_policy == "ALL",
                    )

                elif flag and plugin_manager is not None:
                    result = plugin_manager.suspend(main_debugger, thread, frame, bp_type)
                    if result:
                        frame = result

                # if thread has a suspend flag, we suspend with a busy wait
                if info.pydev_state == STATE_SUSPEND:
                    self.do_wait_suspend(thread, frame, event, arg)
                    return self.trace_dispatch
                else:
                    if not breakpoint and is_line:
                        # No stop from anyone and no breakpoint found in line (cache that).
                        frame_skips_cache[line_cache_key] = 0

            except:
                pydev_log.exception()
                raise

            # step handling. We stop when we hit the right frame
            try:
                should_skip = 0
                if pydevd_dont_trace.should_trace_hook is not None:
                    if self.should_skip == -1:
                        # I.e.: cache the result on self.should_skip (no need to evaluate the same frame multiple times).
                        # Note that on a code reload, we won't re-evaluate this because in practice, the frame.f_code
                        # Which will be handled by this frame is read-only, so, we can cache it safely.
                        if not pydevd_dont_trace.should_trace_hook(frame, filename):
                            # -1, 0, 1 to be Cython-friendly
                            should_skip = self.should_skip = 1
                        else:
                            should_skip = self.should_skip = 0
                    else:
                        should_skip = self.should_skip

                plugin_stop = False
                if should_skip:
                    stop = False

                elif step_cmd in (CMD_STEP_INTO, CMD_STEP_INTO_MY_CODE, CMD_STEP_INTO_COROUTINE):
                    force_check_project_scope = step_cmd == CMD_STEP_INTO_MY_CODE
                    if is_line:
                        if force_check_project_scope or main_debugger.is_files_filter_enabled:
                            stop = not main_debugger.apply_files_filter(frame, frame.f_code.co_filename, force_check_project_scope)
                        else:
                            stop = True

                    elif is_return and frame.f_back is not None:
                        if main_debugger.get_file_type(frame.f_back) == main_debugger.PYDEV_FILE:
                            stop = False
                        else:
                            if force_check_project_scope or main_debugger.is_files_filter_enabled:
                                stop = not main_debugger.apply_files_filter(frame.f_back, frame.f_back.f_code.co_filename, force_check_project_scope)
                            else:
                                stop = True
                    else:
                        stop = False

                    if stop:
                        if step_cmd == CMD_STEP_INTO_COROUTINE:
                            # i.e.: Check if we're stepping into the proper context.
                            f = frame
                            while f is not None:
                                if f is stop_frame:
                                    break
                                f = f.f_back
                            else:
                                stop = False

                    if plugin_manager is not None:
                        result = plugin_manager.cmd_step_into(main_debugger, frame, event, self._args, stop_info, stop)
                        if result:
                            stop, plugin_stop = result

                elif step_cmd in (CMD_STEP_OVER, CMD_STEP_OVER_MY_CODE):
                    # Note: when dealing with a step over my code it's the same as a step over (the
                    # difference is that when we return from a frame in one we go to regular step
                    # into and in the other we go to a step into my code).
                    stop = stop_frame is frame and is_line
                    # Note: don't stop on a return for step over, only for line events
                    # i.e.: don't stop in: (stop_frame is frame.f_back and is_return) as we'd stop twice in that line.

                    if plugin_manager is not None:
                        result = plugin_manager.cmd_step_over(main_debugger, frame, event, self._args, stop_info, stop)
                        if result:
                            stop, plugin_stop = result

                elif step_cmd == CMD_SMART_STEP_INTO:
                    stop = False
                    if info.pydev_smart_step_stop is frame:
                        info.pydev_func_name = '.invalid.'  # Must match the type in cython
                        info.pydev_smart_step_stop = None

                    if is_line or is_exception_event:
                        curr_func_name = frame.f_code.co_name

                        # global context is set with an empty name
                        if curr_func_name in ('?', '<module>') or curr_func_name is None:
                            curr_func_name = ''

                        if curr_func_name == info.pydev_func_name:
                            stop = True

                elif step_cmd in (CMD_STEP_RETURN, CMD_STEP_RETURN_MY_CODE):
                    stop = is_return and stop_frame is frame

                else:
                    stop = False

                if stop and step_cmd != -1 and is_return and IS_PY3K and hasattr(frame, "f_back"):
                    f_code = getattr(frame.f_back, 'f_code', None)
                    if f_code is not None:
                        if main_debugger.get_file_type(frame.f_back) == main_debugger.PYDEV_FILE:
                            stop = False

                if plugin_stop:
                    stopped_on_plugin = plugin_manager.stop(main_debugger, frame, event, self._args, stop_info, arg, step_cmd)
                elif stop:
                    if is_line:
                        self.set_suspend(thread, step_cmd, original_step_cmd=info.pydev_original_step_cmd)
                        self.do_wait_suspend(thread, frame, event, arg)
                    elif is_return:  # return event
                        back = frame.f_back
                        if back is not None:
                            # When we get to the pydevd run function, the debugging has actually finished for the main thread
                            # (note that it can still go on for other threads, but for this one, we just make it finish)
                            # So, just setting it to None should be OK
                            _, back_filename, base = get_abs_path_real_path_and_base_from_frame(back)
                            if (base, back.f_code.co_name) in (DEBUG_START, DEBUG_START_PY3K):
                                back = None

                            elif base == TRACE_PROPERTY:
                                # We dont want to trace the return event of pydevd_traceproperty (custom property for debugging)
                                # if we're in a return, we want it to appear to the user in the previous frame!
                                return None if is_call else NO_FTRACE

                            elif pydevd_dont_trace.should_trace_hook is not None:
                                if not pydevd_dont_trace.should_trace_hook(back, back_filename):
                                    # In this case, we'll have to skip the previous one because it shouldn't be traced.
                                    # Also, we have to reset the tracing, because if the parent's parent (or some
                                    # other parent) has to be traced and it's not currently, we wouldn't stop where
                                    # we should anymore (so, a step in/over/return may not stop anywhere if no parent is traced).
                                    # Related test: _debugger_case17a.py
                                    main_debugger.set_trace_for_frame_and_parents(back)
                                    return None if is_call else NO_FTRACE

                        if back is not None:
                            # if we're in a return, we want it to appear to the user in the previous frame!
                            self.set_suspend(thread, step_cmd, original_step_cmd=info.pydev_original_step_cmd)
                            self.do_wait_suspend(thread, back, event, arg)
                        else:
                            # in jython we may not have a back frame
                            info.pydev_step_stop = None
                            info.pydev_original_step_cmd = -1
                            info.pydev_step_cmd = -1
                            info.pydev_state = STATE_RUN

            except KeyboardInterrupt:
                raise
            except:
                try:
                    pydev_log.exception()
                    info.pydev_original_step_cmd = -1
                    info.pydev_step_cmd = -1
                    info.pydev_step_stop = None
                except:
                    return None if is_call else NO_FTRACE

            # if we are quitting, let's stop the tracing
            if not main_debugger.quitting:
                return self.trace_dispatch
            else:
                return None if is_call else NO_FTRACE
        finally:
            info.is_tracing -= 1