def mt(request):
    return {
        'apertium_api_key': settings.MT_APERTIUM_KEY,
        'microsoft_api_key': settings.MT_MICROSOFT_KEY,
    }