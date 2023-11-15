def secondary_training_status_message(job_description, prev_description):
    """Returns a string contains last modified time and the secondary training job status message.

    Args:
        job_description: Returned response from DescribeTrainingJob call
        prev_description: Previous job description from DescribeTrainingJob call

    Returns:
        str: Job status string to be printed.

    """

    if job_description is None or job_description.get('SecondaryStatusTransitions') is None\
            or len(job_description.get('SecondaryStatusTransitions')) == 0:
        return ''

    prev_description_secondary_transitions = prev_description.get('SecondaryStatusTransitions')\
        if prev_description is not None else None
    prev_transitions_num = len(prev_description['SecondaryStatusTransitions'])\
        if prev_description_secondary_transitions is not None else 0
    current_transitions = job_description['SecondaryStatusTransitions']

    if len(current_transitions) == prev_transitions_num:
        # Secondary status is not changed but the message changed.
        transitions_to_print = current_transitions[-1:]
    else:
        # Secondary status is changed we need to print all the entries.
        transitions_to_print = current_transitions[prev_transitions_num - len(current_transitions):]

    status_strs = []
    for transition in transitions_to_print:
        message = transition['StatusMessage']
        time_str = datetime.utcfromtimestamp(
            time.mktime(job_description['LastModifiedTime'].timetuple())).strftime('%Y-%m-%d %H:%M:%S')
        status_strs.append('{} {} - {}'.format(time_str, transition['Status'], message))

    return '\n'.join(status_strs)