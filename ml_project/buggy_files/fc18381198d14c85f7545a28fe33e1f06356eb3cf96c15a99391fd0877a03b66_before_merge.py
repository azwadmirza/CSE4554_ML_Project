def js_config(request):
    '''
    Generates settings for javascript. Includes things like
    API keys for translaiton services or list of languages they
    support.
    '''
    # Apertium support
    if settings.MT_APERTIUM_KEY is not None and settings.MT_APERTIUM_KEY != '':
        try:
            listpairs = urllib2.urlopen('http://api.apertium.org/json/listPairs?key=%s' % settings.MT_APERTIUM_KEY)
            pairs = listpairs.read()
            parsed = json.loads(pairs)
            apertium_langs = [p['targetLanguage'] for p in parsed['responseData'] if p['sourceLanguage'] == 'en']
        except Exception as e:
            logger.error('failed to get supported languages from Apertium, using defaults (%s)', str(e))
            apertium_langs = ['gl', 'ca', 'es', 'eo']
    else:
        apertium_langs = None

    # Microsoft translator support
    if settings.MT_MICROSOFT_KEY is not None and settings.MT_MICROSOFT_KEY != '':
        try:
            listpairs = urllib2.urlopen('http://api.microsofttranslator.com/V2/Http.svc/GetLanguagesForTranslate?appID=%s' % settings.MT_MICROSOFT_KEY)
            data = listpairs.read()
            parsed = ElementTree.fromstring(data)
            microsoft_langs = [p.text for p in parsed.getchildren()]
        except Exception as e:
            logger.error('failed to get supported languages from Microsoft, using defaults (%s)', str(e))
            microsoft_langs = [
                'ar', 'bg', 'ca', 'zh-CHS', 'zh-CHT', 'cs', 'da', 'nl', 'en',
                'et', 'fi', 'fr', 'de', 'el', 'ht', 'he', 'hi', 'mww', 'hu',
                'id', 'it', 'ja', 'ko', 'lv', 'lt', 'no', 'fa', 'pl', 'pt',
                'ro', 'ru', 'sk', 'sl', 'es', 'sv', 'th', 'tr', 'uk', 'vi'
            ]
    else:
        microsoft_langs = None

    return render_to_response('js/config.js', RequestContext(request, {
            'apertium_langs': apertium_langs,
            'microsoft_langs': microsoft_langs,
        }),
        mimetype = 'application/javascript')