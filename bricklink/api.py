'''
    bricklink.api
    -------------

    A module providing access to the Bricklink API
'''

import json

from rauth import OAuth1Service

from bricklink.exceptions import *
from methods import Orders, Inventory, Catalog, Feedback, Color, Category, PushNotification, Member


class ApiClient:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.service = OAuth1Service(name='bricklink',
                                     consumer_key=consumer_key,
                                     consumer_secret=consumer_secret,
                                     base_url='https://api.bricklink.com/api/store/v1/')

        self.session = self.service.get_session((access_token, access_token_secret))

        self.orders = Orders(self)
        self.inventory = Inventory(self)
        self.catalog = Catalog(self)
        self.feedback = Feedback(self)
        self.color = Color(self)
        self.category = Category(self)
        self.pushnotification = PushNotification(self)
        self.member = Member(self)

    def processResponse(self, response, method, url, params):
        if not 'meta' in response:
            raise BricklinkInvalidResponseException('No meta and/or data key in response')

        meta = response['meta']

        if meta['code'] not in (200, 201, 204):
            if meta['message'] == 'INVALID_URI': raise BricklinkInvalidURIException(meta['description'])
            elif meta['message'] == 'INVALID_REQUEST_BODY': raise BricklinkInvalidRequestBodyException(meta['description'])
            elif meta['message'] == 'PARAMETER_MISSING_OR_INVALID': raise BricklinkParameterMissingOrInvalidException(meta['description'])
            elif meta['message'] == 'BAD_OAUTH_REQUEST': raise BricklinkBadOauthRequestException(meta['description'])
            elif meta['message'] == 'PERMISSION_DENIED': raise BricklinkPermissionDeniedException(meta['description'])
            elif meta['message'] == 'RESOURCE_NOT_FOUND': raise BricklinkResourceNotFoundException(meta['description'])
            elif meta['message'] == 'METHOD_NOT_ALLOWED': raise BricklinkMethodNotAllowedException(meta['description'])
            elif meta['message'] == 'UNSUPPORTED_MEDIA_TYPE': raise BricklinkUnsupportedMediaTypeException(meta['description'])
            elif meta['message'] == 'RESOURCE_UPDATE_NOT_ALLOWED': raise BricklinkResourceUpdateNotAllowedException(meta['description'])
            elif meta['message'] == 'INTERNAL_SERVER_ERROR': raise BricklinkInternalServerErrorException(meta['description'])
            else: raise BricklinkUnspecifiedException(meta['code'], meta['message'], meta['description'])

        data = response['data'] if 'data' in response else []

        return data

    def request(self, method, url, params):
        if method in ('POST', 'PUT', 'DELETE'):
            response = self.session.request(method, url, True, '', data=json.dumps(params), headers={'Content-Type': 'application/json'}).json()
        else:
            response = self.session.request(method, url, True, '', params=params).json()
        return self.processResponse(response, method, url, params)

    def get(self, url, params={}):
        return self.request('GET', url, params)

    def post(self, url, params={}):
        return self.request('POST', url, params)

    def put(self, url, params={}):
        return self.request('PUT', url, params)

    def delete(self, url, params={}):
        return self.request('DELETE', url, params)
