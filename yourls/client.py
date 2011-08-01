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

import sys
import urllib
import urllib2
import json
import re

class YourlsKeywordError(Exception):
    """Used when there are keyword conflicts in requested custom URLs"""
    def __init__(self, url, message):
        self.url = url
        self.message = message
    def __str__(self):
        return repr('Error shortening url %s - %s' % (self.url, self.message))

class YourlsClient():

    def __init__(self, apiurl, username=None, password=None):
        if apiurl is None:
            print "api url is required"
            sys.exit(2)
        else:
            self.apiurl = apiurl

        if username is None or password is None:
            print "username and password are required"
            sys.exit(2)
        else:
            self.username = username
            self.password = password

        self.data_format = 'json'
        self.std_args = {'username':self.username, 'password':self.password, 'format':self.data_format}

    def _send_request(self, args):
        urlargs = urllib.urlencode(self._make_args(args))
        req = urllib2.Request(self.apiurl)
        req.add_data(urlargs)
        r = urllib2.urlopen(req)
        data = r.read()
        return data

    def _make_args(self, new_args):
        return dict(self.std_args.items() + new_args.items())

    def shorten(self, url, custom = None):
        """Request a shortened URL from YOURLS with an optional keyword request

        :param url: The URL to shorten
        :type url: str
        :param custom: The custom keyword to request
        :type custom: str
        :returns: str -- The short URL
        :raises: YourlsKeywordError

        """
        args = {'action':'shorturl','url':url}

        if custom is not None:
            args['keyword'] = custom

        raw_data = json.loads(self._send_request(args))
        if raw_data['status'] == 'fail':
            if re.search('Short URL [a-zA-Z0-9\\-]+ already exists in database', raw_data['message']) is not None:
                raise YourlsKeywordError(url, raw_data['message'])

        return raw_data['shorturl']


    def get_stats(self, shorturl):
        raise NotImplementedError('get_stats has not yet been implemented')

    def expand(self, shorturl):
        raise NotImplementedError('expand has not yet been implemented')
