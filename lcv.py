#!/bin/sh

import getpass
import json
from decimal import Decimal, ROUND_HALF_UP
import locale
from suds.client import Client
from bricklink import exceptions
from bricklink import api
from suds.sax.text import Raw

# BrickLink Library: https://github.com/robbietjuh/py-bricklink/blob/master/bricklink/methods.py

def main():
    print 'Loading API keys from keys.json...'

    with open('keys.json') as data_file:
        keys = json.load(data_file)

    brickset_api_key = keys.get('brickset_api_key')
    bricklink_consumer_key = keys.get('bricklink_consumer_key')
    bricklink_consumer_secret = keys.get('bricklink_consumer_secret')
    bricklink_access_token = keys.get('bricklink_access_token')
    bricklink_access_token_secret = keys.get('bricklink_access_token_secret')

    print 'Let\'s find the value of your collection and the sets you want!'
    print 'Please input the parameters below.'

    brickset_username = raw_input('Brickset Username: ')
    if brickset_api_key is None:
        brickset_api_key = raw_input('Brickset API Key: ')
    if bricklink_consumer_key is None:
        bricklink_consumer_key = raw_input('BrickLink Consumer Key: ')
    if bricklink_consumer_secret is None:
        bricklink_consumer_secret = getpass.getpass('BrickLink Consumer Secret: ')
    if bricklink_access_token is None:
        bricklink_access_token = raw_input('BrickLink Access Token: ')
    if bricklink_access_token_secret is None:
        bricklink_access_token_secret = getpass.getpass('BrickLink Access Token Secret: ')
    want_price_as_new = raw_input('New or used value? \'n\' for new or \'u\' for used: ') == 'n'

    print '\nProcessing your collection...'

    get_sets_value(True, brickset_username, brickset_api_key, want_price_as_new, bricklink_consumer_key, bricklink_consumer_secret, bricklink_access_token, bricklink_access_token_secret)

    print '\nProcessing wanted sets...'

    get_sets_value(False, brickset_username, brickset_api_key, want_price_as_new, bricklink_consumer_key, bricklink_consumer_secret, bricklink_access_token, bricklink_access_token_secret)

def get_sets_value(is_collection, brickset_username, brickset_api_key, want_price_as_new, bricklink_consumer_key, bricklink_consumer_secret, bricklink_access_token, bricklink_access_token_secret):
    # Get value of collection
    sets = get_brickset_sets(brickset_username, brickset_api_key, is_collection)

    sets = get_bricklink_sets(sets,
                       want_price_as_new,
                       bricklink_consumer_key,
                       bricklink_consumer_secret,
                       bricklink_access_token,
                       bricklink_access_token_secret)

    min_value = 0
    max_value = 0
    avg_value = 0
    qty_avg_value = 0
    mvs = sets[0]
    success_count = 0

    for s in sets:
        try:
            #print_price_info(s)
            min_value += round_decimal(s.min_price)
            max_value += round_decimal(s.max_price)
            avg_value += round_decimal(s.avg_price)
            qty_avg_value += round_decimal(s.qty_avg_price)
            temp_max_price = None
            try:
                temp_max_price = mvs.max_price
            except AttributeError as e:
                temp_max_price = None
                mvs = s
            if temp_max_price is not None:
                if round_decimal(s.max_price) > round_decimal(mvs.max_price):
                    mvs = s
            success_count += 1
        except AttributeError as e:
            #print 'Error processing set: ' + str(s.number) + "-" + str(s.numberVariant)
            continue

    locale.setlocale(locale.LC_ALL, '')

    print '\n'
    print 'We were able to process ' + str(success_count) + '/' + str(len(sets)) + (' of the sets you %s!' % ('own' if is_collection else 'want'))
    print 'The minimum value of %s is: ' % ('your collection' if is_collection else 'the sets you want') + locale.currency(round_decimal(min_value), grouping=True)
    print 'The maximum value of %s is: ' % ('your collection' if is_collection else 'the sets you want') + locale.currency(round_decimal(max_value), grouping=True)
    print 'The total average value of %s is: ' % ('your collection' if is_collection else 'the sets you want') + locale.currency(round_decimal(avg_value), grouping=True)
    print 'The total quantity average value of %s is: ' % ('your collection' if is_collection else 'the sets you want') + locale.currency(round_decimal(qty_avg_value),
                                                                                 grouping=True)
    try:
        print ('The most valuable set you %s is: ' % ('own' if is_collection else 'want')) + str(mvs.number) + "-" + str(mvs.numberVariant) + " with a value of " + str(locale.currency(round_decimal(mvs.max_price), grouping=True))
    except AttributeError as e:
        pass


def get_brickset_sets(username, api_key, get_owned):
    print 'Getting Brickset list of sets...'

    brickset_wsdl_url = 'http://brickset.com/api/v2.asmx?WSDL'

    client = Client(brickset_wsdl_url)

    if get_owned:
        # we want the owned sets
        xml_input = """<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope" xmlns:tm="http://microsoft.com/wsdl/mime/textMatching/" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:mime="http://schemas.xmlsoap.org/wsdl/mime/" xmlns:tns="http://brickset.com/api/" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:s="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://schemas.xmlsoap.org/wsdl/soap12/" xmlns:http="http://schemas.xmlsoap.org/wsdl/http/" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" ><SOAP-ENV:Body><tns:getSets xmlns:tns="http://brickset.com/api/"><tns:apiKey>%s</tns:apiKey><tns:userHash></tns:userHash><tns:userHash></tns:userHash><tns:query></tns:query><tns:query></tns:query><tns:theme></tns:theme><tns:theme></tns:theme><tns:subtheme></tns:subtheme><tns:subtheme></tns:subtheme><tns:setNumber></tns:setNumber><tns:setNumber></tns:setNumber><tns:year></tns:year><tns:year></tns:year><tns:owned>1</tns:owned><tns:wanted></tns:wanted><tns:wanted></tns:wanted><tns:orderBy></tns:orderBy><tns:orderBy></tns:orderBy><tns:pageSize>1000</tns:pageSize><tns:pageNumber></tns:pageNumber><tns:pageNumber></tns:pageNumber><tns:userName>%s</tns:userName></tns:getSets></SOAP-ENV:Body></SOAP-ENV:Envelope>""" % (api_key, username)
    else:
        # we want the wanted sets
        xml_input = """<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope" xmlns:tm="http://microsoft.com/wsdl/mime/textMatching/" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:mime="http://schemas.xmlsoap.org/wsdl/mime/" xmlns:tns="http://brickset.com/api/" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:s="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://schemas.xmlsoap.org/wsdl/soap12/" xmlns:http="http://schemas.xmlsoap.org/wsdl/http/" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" ><SOAP-ENV:Body><tns:getSets xmlns:tns="http://brickset.com/api/"><tns:apiKey>%s</tns:apiKey><tns:userHash></tns:userHash><tns:userHash></tns:userHash><tns:query></tns:query><tns:query></tns:query><tns:theme></tns:theme><tns:theme></tns:theme><tns:subtheme></tns:subtheme><tns:subtheme></tns:subtheme><tns:setNumber></tns:setNumber><tns:setNumber></tns:setNumber><tns:year></tns:year><tns:year></tns:year><tns:owned></tns:owned><tns:owned></tns:owned><tns:wanted>1</tns:wanted><tns:orderBy></tns:orderBy><tns:orderBy></tns:orderBy><tns:pageSize>1000</tns:pageSize><tns:pageNumber></tns:pageNumber><tns:pageNumber></tns:pageNumber><tns:userName>%s</tns:userName></tns:getSets></SOAP-ENV:Body></SOAP-ENV:Envelope>""" % (api_key, username)

    xml = Raw(xml_input)
    response = client.service.getSets(__inject={'msg': xml})
    # print response

    return_sets = response.sets

    #for set in return_sets:
    #    print set.number

    return return_sets


def get_bricklink_sets(sets, new_or_used, consumer_key, consumer_secret, token, token_secret):
    print 'Getting BrickLink price info...'

    bricklink_api_url = 'https://api.bricklink.com/api/store/v1'

    client = api.ApiClient(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=token,
        access_token_secret=token_secret
    )

    new_param = 'U'
    if new_or_used:
        new_param = 'N'

    for set in sets:
        try:
            set_id = str(set.number) + "-" + str(set.numberVariant)
            json_response = client.catalog.getPriceGuide(item_type='SET', item_no=set_id, new_or_used=new_param)
            parsed_response = json.dumps(json_response)
            set_price_info(set, parsed_response)
            # print_price_info(set)
        except exceptions.BricklinkParameterMissingOrInvalidException as e:
            continue
        except exceptions.BricklinkResourceNotFoundException as e:
            continue

    return sets


def round_decimal(x):
    return Decimal(x).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)

def set_price_info(set, price_json):
    set.__dict__.update(json.loads(price_json))

def print_price_info(set):
    print str(set.number) + ', min price: $' + str(round_decimal(
            set.min_price)) + ", max price: $" + str(round_decimal(
            set.max_price)) + ", avg price: $" + str(round_decimal(
            set.avg_price)) + ", qty avg price: $" + str(round_decimal(set.qty_avg_price))


if __name__ == "__main__":
    main()
