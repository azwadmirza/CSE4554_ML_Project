def _assemble_contours(points_iterator):
    current_index = 0
    contours = {}
    starts = {}
    ends = {}
    for from_point, to_point in points_iterator:
        # Ignore degenerate segments.
        # This happens when (and only when) one vertex of the square is
        # exactly the contour level, and the rest are above or below.
        # This degenerate vertex will be picked up later by neighboring
        # squares.
        if from_point == to_point:
            continue

        tail_data = starts.get(to_point)
        head_data = ends.get(from_point)

        if tail_data is not None and head_data is not None:
            tail, tail_num = tail_data
            head, head_num = head_data
            # We need to connect these two contours.
            if tail is head:
                # We need to closed a contour.
                # Add the end point, and remove the contour from the
                # 'starts' and 'ends' dicts.
                head.append(to_point)
                del starts[to_point]
                del ends[from_point]
            else:  # tail is not head
                # We need to join two distinct contours.
                # We want to keep the first contour segment created, so that
                # the final contours are ordered left->right, top->bottom.
                if tail_num > head_num:
                    # tail was created second. Append tail to head.
                    head.extend(tail)
                    # remove all traces of tail:
                    del starts[to_point]
                    try:
                        del ends[tail[-1]]
                    except KeyError:
                        pass
                    del contours[tail_num]
                    # remove the old end of head and add the new end.
                    del ends[from_point]
                    ends[head[-1]] = (head, head_num)
                else:  # tail_num <= head_num
                    # head was created second. Prepend head to tail.
                    tail.extendleft(reversed(head))
                    # remove all traces of head:
                    del starts[head[0]]
                    del ends[from_point]
                    del contours[head_num]
                    # remove the old start of tail and add the new start.
                    del starts[to_point]
                    starts[tail[0]] = (tail, tail_num)
        elif tail_data is None and head_data is None:
            # we need to add a new contour
            current_index += 1
            new_num = current_index
            new_contour = deque((from_point, to_point))
            contours[new_num] = new_contour
            starts[from_point] = (new_contour, new_num)
            ends[to_point] = (new_contour, new_num)
        elif tail_data is not None and head_data is None:
            tail, tail_num = tail_data
            # We've found a single contour to which the new segment should be
            # prepended.
            tail.appendleft(from_point)
            del starts[to_point]
            starts[from_point] = (tail, tail_num)
        elif tail_data is None and head_data is not None:
            head, head_num = head_data
            # We've found a single contour to which the new segment should be
            # appended
            head.append(to_point)
            del ends[from_point]
            ends[to_point] = (head, head_num)
    # end iteration over from_ and to_ points

    return [np.array(contour) for (num, contour) in sorted(contours.items())]