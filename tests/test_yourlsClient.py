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
#       Tim Flink <tflink@redhat.com> - original test unit
#       Jordi Llonch <llonchj@gmail.com> - test refactoring using unittest

import os
import json
import string
import random
import httplib
import urlparse
import unittest

import yourls.client
from yourls import YourlsError, YourlsOperationError

test_baseurl = os.environ.get('YOURLS_TEST_BASEURL', 
    'http://localhost/yourls/')
test_apiurl = os.environ.get('YOURLS_TEST_APIURL', 
    urlparse.urljoin(test_baseurl, 'yourls-api.php'))
    
test_user = os.environ.get('YOURLS_TEST_USER', 'username')
test_pass = os.environ.get('YOURLS_TEST_PASSWORD', 'password')
test_token = os.environ.get('YOURLS_TEST_TOKEN', None)

def keyword_generator(size=15, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def setUp():
    print "Using test server..."
    print "API Url: %s" % test_apiurl
    print "Username: %s" % test_user
    print "Password: %s" % ("*" * len(test_pass))
    print
    if test_token is None:
        msg = " Define environ 'YOURLS_TEST_TOKEN' to test PasswordLess API access "
        print "*" * len(msg)
        print msg
        print "*" * len(msg)
        print

class YourlsTest(unittest.TestCase):
    url = "http://www.google.com/"
    
    def shorturl_and_expand(self, client, url=None):
        if url is None:
            url = self.url

        keyword = keyword_generator()

        result = client.shorturl(url, keyword=keyword)
        return client.expand(result)
        
    def browse(self, url):
        parsed_url = urlparse.urlparse(url)
        conn = httplib.HTTPConnection(parsed_url.hostname)
        conn.request("GET", parsed_url.path)
        return conn.getresponse()

    def test_missing_credentials(self):
        self.assertRaises(YourlsError, 
            yourls.client.YourlsClient, (test_apiurl,))

    def test_missing_username(self):
        self.assertRaises(YourlsError, 
            yourls.client.YourlsClient, (test_apiurl, None, test_pass))

    def test_missing_password(self):
        self.assertRaises(YourlsError, 
            yourls.client.YourlsClient, (test_apiurl, test_user, None))

    def test_invalid_yourls_server(self):
        self.assertRaises(YourlsError, 
            yourls.client.YourlsClient, (None,))

    def test_invalid_token(self):
        self.assertRaises(YourlsError, 
            yourls.client.YourlsClient, (test_apiurl,), 
            dict(token=str(test_token) + "xxx"))

    def test_invalid_user(self):
        client = yourls.client.YourlsClient(test_apiurl, 
            username=test_user + "xxx", password=test_pass)
        self.assertRaises(YourlsOperationError, client.shorturl, (self.url,))

    def test_invalid_password(self):
        client = yourls.client.YourlsClient(test_apiurl, 
            username=test_user, password=test_pass + "xxx")
        self.assertRaises(YourlsOperationError, client.shorturl, (self.url,))

    def test_non_existing_keyword(self):
        client = yourls.client.YourlsClient(test_apiurl, 
            username=test_user, password=test_pass)
        for i in range(1, 10):
            keyword = keyword_generator(30)
            self.assertRaises(YourlsOperationError, 
                client.expand, (keyword,))

    def test_token_shorturl_and_expand(self):
        assert test_token

        client = yourls.client.YourlsClient(test_apiurl, token=test_token)
        self.assertEqual(self.url, self.shorturl_and_expand(client))

    def test_login_shorturl_and_expand(self):
        client = yourls.client.YourlsClient(test_apiurl, 
            username=test_user, password=test_pass)
        self.assertEqual(self.url, self.shorturl_and_expand(client))

    def test_stats(self):
        client = yourls.client.YourlsClient(test_apiurl, 
            username=test_user, password=test_pass)
        
        keyword = keyword_generator()
        url = "http://www.gmail.com/"
        title = "i am the title"

        shorturl = client.shorturl(url, keyword=keyword, title=title)
        
        result = client.url_stats(shorturl)

        self.assertTrue(isinstance(result, dict))

        #
        self.assertEqual(result.get("url", None), url)
        self.assertEqual(result.get("title", None), title)
        clicks = long(result.get("clicks"))

        #test the clicks increases when navigate
        response = self.browse(shorturl)
        self.assertTrue(response.status == 301)
        
        result = client.url_stats(shorturl)
        clicks_new = long(result.get("clicks"))
        
        self.assertTrue(clicks_new == clicks + 1)

if __name__ == '__main__':
    unittest.main()
