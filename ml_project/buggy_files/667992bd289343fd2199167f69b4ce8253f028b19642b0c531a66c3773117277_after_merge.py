def execute_chunk(chunk, executor=None,
                  ref_counts=None, chunk_result=None,
                  finishes=None, visited=None, q=None,
                  lock=None, semaphore=None, has_error=None,
                  preds=None, succs=None, mock=False, sparse_mock_percent=1.0):
    try:
        with lock:
            if (chunk.key, chunk.id) in visited:
                return
            visited.add((chunk.key, chunk.id))
            finished = finishes.get(chunk.key)
        if not finished:
            if not mock:
                # do real execution
                if chunk.key not in chunk_result:
                    executor.handle(chunk, chunk_result)
            else:
                percent = sparse_mock_percent if chunk.op.sparse else 1.0
                # we put the estimated size of data into the chunk_result
                chunk_result[chunk.key] = np.prod(chunk.shape) * chunk.dtype.itemsize * percent
            with lock:
                for output in chunk.op.outputs:
                    finishes[output.key] = True
                    if output.key in ref_counts and ref_counts[output.key] == 0 and \
                            output.key in chunk_result:
                        # some op have more than 1 outputs,
                        # and some of the outputs are not in the result ones
                        del chunk_result[output.key]

        for pred_key in preds[chunk.key]:
            with lock:
                if pred_key not in ref_counts:
                    continue
                ref_counts[pred_key] -= 1
                if ref_counts[pred_key] == 0:
                    del chunk_result[pred_key]

        for succ in succs[chunk.key, chunk.id]:
            with lock:
                if (succ.key, succ.id) in visited:
                    continue
                if len(preds[succ.key]) == 0 or \
                        all(finishes.get(k, False) for k in preds[succ.key]):
                    q.insert(0, succ)
    except Exception:
        has_error.set()
        raise
    finally:
        semaphore.release()