def response(resp):
    """Get response from google's search request"""
    results = []

    # detect google sorry
    resp_url = urlparse(resp.url)
    if resp_url.netloc == 'sorry.google.com' or resp_url.path == '/sorry/IndexRedirect':
        raise RuntimeWarning('sorry.google.com')

    if resp_url.path.startswith('/sorry'):
        raise RuntimeWarning(gettext('CAPTCHA required'))

    # which subdomain ?
    # subdomain = resp.search_params.get('google_subdomain')

    # convert the text to dom
    dom = html.fromstring(resp.text)

    # results --> answer
    answer = eval_xpath(dom, '//div[contains(@class, "LGOjhe")]//text()')
    if answer:
        results.append({'answer': ' '.join(answer)})
    else:
        logger.debug("did not found 'answer'")

    # results --> number_of_results
    try:
        _txt = eval_xpath(dom, '//div[@id="result-stats"]//text()')[0]
        _digit = ''.join([n for n in _txt if n.isdigit()])
        number_of_results = int(_digit)
        results.append({'number_of_results': number_of_results})

    except Exception as e:  # pylint: disable=broad-except
        logger.debug("did not 'number_of_results'")
        logger.error(e, exc_info=True)

    # parse results
    for result in eval_xpath(dom, results_xpath):

        # google *sections*
        if extract_text(eval_xpath(result, g_section_with_header)):
            logger.debug("ingoring <g-section-with-header>")
            continue

        try:
            title_tag = eval_xpath(result, title_xpath)
            if not title_tag:
                # this not one of the common google results *section*
                logger.debug('ingoring <div class="g" ../> section: missing title')
                continue
            title = extract_text(title_tag[0])
            url = eval_xpath(result, href_xpath)[0]
            content = extract_text_from_dom(result, content_xpath)
            results.append({
                'url': url,
                'title': title,
                'content': content
            })
        except Exception as e:  # pylint: disable=broad-except
            logger.error(e, exc_info=True)
            # from lxml import etree
            # logger.debug(etree.tostring(result, pretty_print=True))
            # import pdb
            # pdb.set_trace()
            continue

    # parse suggestion
    for suggestion in eval_xpath(dom, suggestion_xpath):
        # append suggestion
        results.append({'suggestion': extract_text(suggestion)})

    for correction in eval_xpath(dom, spelling_suggestion_xpath):
        results.append({'correction': extract_text(correction)})

    # return results
    return results