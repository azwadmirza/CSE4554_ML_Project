def results_thread_main(strategy):
    while True:
        try:
            result = strategy._final_q.get()
            if isinstance(result, StrategySentinel):
                break
            else:
                strategy._results_lock.acquire()
                # only handlers have the listen attr, so this must be a handler
                # we split up the results into two queues here to make sure
                # handler and regular result processing don't cross wires
                if 'listen' in result._task_fields:
                    strategy._handler_results.append(result)
                else:
                    strategy._results.append(result)
                strategy._results_lock.release()
        except (IOError, EOFError):
            break
        except Queue.Empty:
            pass