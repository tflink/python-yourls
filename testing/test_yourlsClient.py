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
from yourls.client import YourlsKeywordError as YourlsKeywordError
import json

test_baseurl = 'http://localhost/yourls/'
test_apiurl = test_baseurl + 'yourls-api.php'
test_user = 'username'
test_pass = 'password'
test_urltitle = 'testshort'

test_url1 = 'http://testhost.fedoraproject.org/dir/subdir/file.html'
test_url2 = 'http://testhost.fedoraproject.org/dir/subdir/anotherfile.html'

url_data = {1:test_url1, 2:test_url2}

#{u'status': u'fail', u'code': u'error:url', u'title': u'Fedora People', u'url': {u'keyword': '', u'title': u'Fedora People', u'url': u'http://tflink.fedorapeople.org/', u'ip': u'192.168.122.1', u'date': u'2011-07-25 13:30:32', u'clicks': u'3'}, u'shorturl': u'http://192.168.122.202/yourls/2', u'message': u'http://tflink.fedorapeople.org/ already exists in database', u'statusCode': 200}
def make_json_shorten(status, url, shorturl, code = None, message = None):
    if message == None:
        message = 'no message'

    url_data = {'keyword':'', 'title':test_urltitle, 'url':url, 'ip':'127.0.0.1', 'date':'now', 'clicks':'1'}
    data = {'status':status, 'title':test_urltitle, 'url':url_data, 'shorturl':shorturl, 'message':message, 'statuscode':200}
    if code is not None:
        data['code'] = code
    return json.dumps(data)

def mock_shorturl(args):
    for short, url in url_data.iteritems():
        if args['url'] == url:
            return make_json_shorten('success', url, test_baseurl + str(short))

def mock_short_keyworderror(args):
    return make_json_shorten('fail', test_url1, 1, code = 'error:url', message = 'Short URL 1 already exists in database or is reserved')

class TestYourlsClient():

    def setup_method(self, method):
        self.testclient = yourls.client.YourlsClient(test_apiurl, test_user, test_pass)

    def test_shorten_url(self, monkeypatch):
        
        monkeypatch.setattr(self.testclient, '_send_request', mock_shorturl)

        ref_shorturl = test_baseurl + '1'
        test_url = 'http://testhost.fedoraproject.org/dir/subdir/file.html'
        shorturl = self.testclient.shorten(test_url)

        assert shorturl == ref_shorturl

    def test_shorten_second_url(self, monkeypatch):
        monkeypatch.setattr(self.testclient, '_send_request', mock_shorturl)

        ref_shorturl = test_baseurl + '2'
        test_url = 'http://testhost.fedoraproject.org/dir/subdir/anotherfile.html'
        shorturl = self.testclient.shorten(test_url)

        assert shorturl == ref_shorturl

    def test_make_shorten_args(self):
        ref_args = {'username':test_user, 'password':test_pass, 'format':'json', 'action':'shorturl', 'url':test_url1}
        ref_newargs = {'action':'shorturl', 'url':test_url1}

        test_args = self.testclient._make_args(ref_newargs)

        assert ref_args == test_args

#    with pytest.raises(Exception) as excinfo:
    @pytest.mark.xfail
    def test_reserved_keyword(self, monkeypatch):
        monkeypatch.setattr(self.testclient, '_send_request', mock_short_keyworderror)
        self.testclient.shorten(test_url1)
