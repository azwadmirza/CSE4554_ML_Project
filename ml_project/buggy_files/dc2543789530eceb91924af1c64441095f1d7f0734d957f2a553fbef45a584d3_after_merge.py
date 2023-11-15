def _AtCoderProblemContentPartial_from_row(tr: bs4.Tag):
    tds = tr.find_all('td')
    assert 4 <= len(tds) <= 5
    path = tds[1].find('a')['href']
    problem = AtCoderProblem.from_url('https://atcoder.jp' + path)
    assert problem is not None
    alphabet = tds[0].text
    name = tds[1].text
    if tds[2].text.endswith(' msec'):
        time_limit_msec = int(utils.remove_suffix(tds[2].text, ' msec'))
    elif tds[2].text.endswith(' sec'):
        time_limit_msec = int(float(utils.remove_suffix(tds[2].text, ' sec')) * 1000)
    else:
        assert False
    memory_limit_byte = int(float(utils.remove_suffix(tds[3].text, ' MB')) * 1000 * 1000)  # TODO: confirm this is MB truly, not MiB
    if len(tds) == 5:
        assert tds[4].text.strip() in ('', 'Submit', '提出')

    self = AtCoderProblemContentPartial(alphabet, memory_limit_byte, name, problem, time_limit_msec)
    problem._cached_content = self
    return self