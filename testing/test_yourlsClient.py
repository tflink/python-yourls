# test_yourlsClient.py
#  - tests for the python yourls client
#
# Copyright 2011, Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Author:
#       Tim Flink <tflink@redhat.com>


import pytest
import yourls.client
from yourls import YourlsError, YourlsOperationError
import json

test_baseurl = 'http://localhost/yourls/'
test_apiurl = test_baseurl + 'yourls-api.php'
test_user = 'username'
test_pass = 'password'
test_urltitle = 'testshort'
test_numclicks = 3

test_url1 = 'http://testhost.fedoraproject.org/dir/subdir/file.html'
test_url2 = 'http://testhost.fedoraproject.org/dir/subdir/anotherfile.html'

url_data = {1:test_url1, 2:test_url2}

#{u'status': u'fail', u'code': u'error:url', u'title': u'Fedora People', u'url': {u'keyword': '', u'title': u'Fedora People', u'url': u'http://tflink.fedorapeople.org/', u'ip': u'192.168.122.1', u'date': u'2011-07-25 13:30:32', u'clicks': u'3'}, u'shorturl': u'http://192.168.122.202/yourls/2', u'message': u'http://tflink.fedorapeople.org/ already exists in database', u'statusCode': 200}
def make_json_response(status, url, shorturl, code = None, message = None,
                        statuscode = None):
    if not message:
        message = 'no message'
    if not statuscode:
        statuscode = 200

    url_data = {'keyword':'', 'title':test_urltitle, 'url':url, 'ip':'127.0.0.1',
                'date':'now', 'clicks':'1'}
    data = {'status':status, 'title':test_urltitle, 'url':url_data,
            'shorturl':shorturl, 'message':message, 'statuscode':statuscode}
    if code is not None:
        data['code'] = code
    return json.dumps(data)

def make_json_error(errorCode, message):
    data = {'message': message, 'errorCode': errorCode}
    return json.dumps(data)

def make_json_expand(baseurl, keyword, longurl):
    data = {'shorturl':(baseurl+str(keyword)), 'longurl':longurl,
            'keyword':keyword, 'message':'success', 'statusCode':200}
    return json.dumps(data)

def make_json_urlstats(baseurl, keyword, longurl, clicks, isError = False):
    if not isError:
        url_data = {'title' : 'Testing Link Title' , 'url' : longurl,
                    'ip' : '127.0.0.1', 'shorturl' : test_baseurl + str(keyword),
                    'clicks' : clicks }
        data = {'message' : 'success', 'link' : url_data, 'statusCode' : 200}
    else:
        data = {'message' : 'Error: short URL not found', 'statusCode' : 404}

    return json.dumps(data)

def mock_request_error(args):
        return make_json_error('Invalid username or password', 403)

def mock_request(args):
    if args['action'] == 'shorturl':
        for short, url in url_data.iteritems():
            if args['url'] == url:
                return make_json_response('success', url, test_baseurl + str(short))
    elif args['action'] == 'expand':
        for short, url in url_data.iteritems():
            if args['shorturl'] == short:
                return make_json_expand(test_baseurl, short, url)
    elif args['action'] == 'url-stats':
        for short, url in url_data.iteritems():
            if args['shorturl'] == short:
                return make_json_urlstats( test_baseurl, short, url, test_numclicks,
                                           isError = False)

def mock_short_keyworderror(args):
    return make_json_response('fail', test_url1, 1, code = 'error:keyword',
            message = 'Short URL 1 already exists in database or is reserved')

def mock_request_404(args):
    code_name = "statusCode"
    if args['action'] == 'expand':
        code_name = "errorCode"
    return json.dumps({ code_name : 404, 'message' : 'Error: short URL not found',
                        'keyword' : args['shorturl']})

class TestYourlsClient():

    def setup_method(self, method):
        self.testclient = yourls.client.YourlsClient(test_apiurl, test_user, test_pass)

    def test_shorten_url(self, monkeypatch):
        monkeypatch.setattr(self.testclient, '_send_request', mock_request)

        ref_shorturl = test_baseurl + '1'
        test_url = 'http://testhost.fedoraproject.org/dir/subdir/file.html'
        shorturl = self.testclient.shorten(test_url)

        assert shorturl == ref_shorturl

    def test_shorten_second_url(self, monkeypatch):
        monkeypatch.setattr(self.testclient, '_send_request', mock_request)

        ref_shorturl = test_baseurl + '2'
        test_url = 'http://testhost.fedoraproject.org/dir/subdir/anotherfile.html'
        shorturl = self.testclient.shorten(test_url)

        assert shorturl == ref_shorturl

    def test_make_shorten_args(self):
        ref_args = {'username':test_user, 'password':test_pass, 'format':'json',
                    'action':'shorturl', 'url':test_url1}
        ref_newargs = {'action':'shorturl', 'url':test_url1}

        test_args = self.testclient._make_args(ref_newargs)

        assert ref_args == test_args

    def test_shorten_used_keyword(self, monkeypatch):
        monkeypatch.setattr(self.testclient, '_send_request', mock_short_keyworderror)
        with pytest.raises(YourlsOperationError):
            self.testclient.shorten(test_url1)

    def test_shorten_invalid_user(self, monkeypatch):
        monkeypatch.setattr(self.testclient, '_send_request', mock_request_error)
        with pytest.raises(YourlsOperationError):
            self.testclient.shorten(test_url1)

    def test_expand_url(self, monkeypatch):
        monkeypatch.setattr(self.testclient, '_send_request', mock_request)
        ref_shorturl = 1

        test_longurl = self.testclient.expand(ref_shorturl)

        assert test_longurl == url_data[ref_shorturl]

    def test_expand_nonexistant_url(self, monkeypatch):
        monkeypatch.setattr(self.testclient, '_send_request', mock_request_404)
        ref_madeupkeyword= 'blahdontexist'
        with pytest.raises(YourlsOperationError):
            self.testclient.expand(ref_madeupkeyword)

    def test_url_stats(self, monkeypatch):
        monkeypatch.setattr(self.testclient, '_send_request', mock_request)
        ref_shorturl = 1

        test_data = self.testclient.get_url_stats(ref_shorturl)

        assert test_data['clicks'] == test_numclicks

    def test_stats_nonextant_url(self, monkeypatch):
        monkeypatch.setattr(self.testclient, '_send_request', mock_request_404)
        ref_madeupkeyword= 'blahdontexist'
        with pytest.raises(YourlsOperationError):
            self.testclient.get_url_stats(ref_madeupkeyword)

    def test_with_empty_apiurl(self):
        with pytest.raises(YourlsError):
            yourls.client.YourlsClient('', test_user, test_pass)

    def test_with_no_username(self):
        with pytest.raises(YourlsError):
            yourls.client.YourlsClient(test_apiurl, '', test_pass)

    def test_with_no_password(self):
        with pytest.raises(YourlsError):
            yourls.client.YourlsClient(test_apiurl, test_user, '')


