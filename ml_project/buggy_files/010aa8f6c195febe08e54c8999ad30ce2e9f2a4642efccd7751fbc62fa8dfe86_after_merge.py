def send_sms(profile, body, to, from_):
    '''
    Send an sms

    CLI Example:

        twilio.send_sms my-twilio-account 'Test sms' '+18019999999' '+18011111111'
    '''
    ret = {}
    ret['message'] = {}
    ret['message']['sid'] = None
    client = _get_twilio(profile)
    try:
        if TWILIO_5:
            message = client.sms.messages.create(body=body, to=to, from_=from_)
        else:
            message = client.messages.create(body=body, to=to, from_=from_)
    except TwilioRestException as exc:
        ret['_error'] = {}
        ret['_error']['code'] = exc.code
        ret['_error']['msg'] = exc.msg
        ret['_error']['status'] = exc.status
        log.debug('Could not send sms. Error: %s', ret)
        return ret
    ret['message'] = {}
    ret['message']['sid'] = message.sid
    ret['message']['price'] = message.price
    ret['message']['price_unit'] = message.price_unit
    ret['message']['status'] = message.status
    ret['message']['num_segments'] = message.num_segments
    ret['message']['body'] = message.body
    ret['message']['date_sent'] = six.text_type(message.date_sent)
    ret['message']['date_created'] = six.text_type(message.date_created)
    log.info(ret)
    return ret