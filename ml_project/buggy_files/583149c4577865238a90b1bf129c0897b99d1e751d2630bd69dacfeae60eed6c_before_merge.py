def _AtCoderProblemContent_parse_partial(soup: bs4.BeautifulSoup, problem: 'AtCoderProblem') -> AtCoderProblemContentPartial:
    h2 = soup.find('span', class_='h2')

    alphabet, _, name = h2.text.partition(' - ')

    time_limit, memory_limit = h2.find_next_sibling('p').text.split(' / ')
    for time_limit_prefix in ('実行時間制限: ', 'Time Limit: '):
        if time_limit.startswith(time_limit_prefix):
            break
    else:
        assert False
    time_limit_msec = int(float(utils.remove_suffix(utils.remove_prefix(time_limit, time_limit_prefix), ' sec')) * 1000)

    for memory_limit_prefix in ('メモリ制限: ', 'Memory Limit: '):
        if memory_limit.startswith(memory_limit_prefix):
            break
    else:
        assert False
    memory_limit_byte = int(float(utils.remove_suffix(utils.remove_prefix(memory_limit, memory_limit_prefix), ' MB')) * 1000 * 1000)

    return AtCoderProblemContentPartial(alphabet, memory_limit_byte, name, problem, time_limit_msec)