# client.py
#  - Python client for yourls
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

"""
.. module:: yourls.client
   :synopsis: A simple client for the YOURLS URL shortener

.. moduleauthor:: Tim Flink <tflink@redhat.com>
"""

import urllib
import urllib2
import json
from yourls import YourlsError, YourlsOperationError

class YourlsClient():

    def __init__(self, apiurl, username=None, password=None, token=None):
        """The use of a username/password combo or a signature token is required

        :param apiurl: The location of the api php file
        :param username: The username to login with (not needed with signature token)
        :param password: The password to login with (not needed with signature token)
        :param token: The signature token to use (not needed with username/password combo)

        :throws: YourlsError for incorrent parameters
        """

        self.data_format = 'json'

        if not apiurl:
            raise YourlsError("An api url is required")
        self.apiurl = apiurl

        if not username or not password:
            if not token:
                raise YourlsError("username and password or signature token are required")
            else:
                self.std_args = {'signature' : token, 'format' : self.data_format}
        else:
            self.username = username
            self.password = password
            self.std_args = {'username':self.username, 'password':self.password,
                             'format':self.data_format}

    def _send_request(self, args):
        urlargs = urllib.urlencode(self._make_args(args))
        req = urllib2.Request(self.apiurl)
        req.add_data(urlargs)
        r = urllib2.urlopen(req)
        data = r.read()
        print data
        return data

    def _make_args(self, new_args):
        return dict(self.std_args.items() + new_args.items())

    def shorten(self, url, custom = None, title = None):
        """Request a shortened URL from YOURLS with an optional keyword request

        :param url: The URL to shorten
        :type url: str
        :param custom: The custom keyword to request
        :type custom: str
        :param title: Use the given title instead of download it from the URL, this will increase performances
        :type title: str
        :returns: str -- The short URL
        :raises: YourlsOperationError

        """
        args = {'action':'shorturl','url':url}

        if custom:
            args['keyword'] = custom

        if title:
            args['title'] = title

        # shorten
        raw_data = json.loads(self._send_request(args))

        # parse result
        if 'errorCode' in raw_data:
            raise YourlsOperationError(url, raw_data['message'])

        if raw_data['status'] == 'fail' and raw_data['code'] == 'error:keyword':
            raise YourlsOperationError(url, raw_data['message'])

        if not 'shorturl' in raw_data:
            raise YourlsOperationError(url, 'Unknown error: %s' % raw_data['message'])

        return raw_data['shorturl']


    def expand(self, shorturl):
        """Expand a shortened URL to its original form

        :param shorturl: The URL to expand
        :returns: str -- The expanded URL
        :raises: YourlsOperationError

        """
        args = {'action' : 'expand', 'shorturl' : shorturl, 'format' : 'json'}

        raw_data = json.loads(self._send_request(args))

        if 'errorCode' in raw_data:
            raise YourlsOperationError(shorturl, raw_data['message'])

        if not 'longurl' in raw_data:
            raise YourlsOperationError(shorturl, raw_data['message'])

        return raw_data['longurl']

    def get_url_stats(self, shorturl):
        """Get statistics about a shortened URL

        :param shorturl: The URL to expand
        :returns: a list of stuff - FIXME, this isn't complete
        :raises: YourlsOperationError

        """

        args = {'action' : 'url-stats', 'shorturl' : shorturl, 'format' : 'json'}

        raw_data = json.loads(self._send_request(args))
        print raw_data

        if 'errorCode' in raw_data:
            raise YourlsOperationError(shorturl, raw_data['message'])

        if raw_data['statusCode'] != 200:
            raise YourlsOperationError(shorturl, raw_data['message'])

        return raw_data['link']
