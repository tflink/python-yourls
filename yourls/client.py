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
import json
import urllib
import urllib2

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
        """Encapsulates the actual sending of a request to a YOURLS instance

        :param args: The arguments to send to YOURLS

        """
        urlargs = urllib.urlencode(self._make_args(args))
        req = urllib2.Request(self.apiurl)
        req.add_data(urlargs)
        r = urllib2.urlopen(req)
        data = r.read()
        return data


    def _make_args(self, new_args):
        """Convenience method for putting args into the proper format

        :param new_args: Dictionary containing the args to pass on

        """
        return dict(self.std_args.items() + new_args.items())


    def _base_request(self, args, url):
        """Encapsulates common code and error handling for the access methods

        :param args: The arguments to send to YOURLS
        :param url: The url (short or long) arg being used in the request
        :raises: YourlsOperationError

        """
        try:
            data = json.loads(self._send_request(args))
        except urllib2.URLError as error:
            raise YourlsOperationError(url, str(error))

        if 'errorCode' in data:
            raise YourlsOperationError(url, data['message'])

        return data


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
        raw_data = self._base_request(args, url)

        # parse result
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

        raw_data = self._base_request(args, shorturl)

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

        raw_data = self._base_request(args, shorturl)

        if raw_data['statusCode'] != 200:
            raise YourlsOperationError(shorturl, raw_data['message'])

        return raw_data['link']

def get_server(apiurl, **kwargs):
    kw = dict(apiurl=apiurl)
    for key in ["username", "password", "token"]:
        value = kwargs.get(key, None)
        if value:
            kw[key] = value
    return YourlsClient(**kw)

def shorten(url, keyword, title=None, server=None, **kwargs):
    if server is None:
        server = get_server(**kwargs)
    return server.shorten(url, custom=keyword, title=title)

def expand(url, server=None, **kwargs):
    if server is None:
        server = get_server(**kwargs)
    return server.expand(url)

def get_url_stats(url, server=None, **kwargs):
    if server is None:
        server = get_server(**kwargs)
    return server.get_url_stats(url)

def set_shorturl_parser(parser):
    parser.add_argument("--apiurl", metavar="uri",
        default="http://127.0.0.1/yourls-api.php",
        help="Yourls API URL (%(default)s)")
    parser.add_argument("--token", help="Token")
    parser.add_argument("--username", help="Username")
    parser.add_argument("--password", help="Password")

def main():
    """YourlsClient command line access"""
    import argparse

    parser = argparse.ArgumentParser(description='Yourls Client')

    subparsers = parser.add_subparsers(dest="command")

    #
    #shorten command
    parser_shorten = subparsers.add_parser('shorten', help="shorten url")

    set_shorturl_parser(parser_shorten)

    parser_shorten.add_argument("--keyword", type=unicode, help="keyword")
    parser_shorten.add_argument("--title", type=unicode, help="title")
    parser_shorten.add_argument("url", type=unicode, help="url")

    parser_shorten.set_defaults(func=shorten)

    #
    #expand command
    parser_expand = subparsers.add_parser('expand', help="expand url")

    set_shorturl_parser(parser_expand)

    parser_expand.add_argument("url", type=unicode, help="url")

    parser_expand.set_defaults(func=expand)

    #
    #get_url_stats command
    parser_get_url_stats = subparsers.add_parser(
        'get_url_stats', help="get_url_stats url")

    set_shorturl_parser(parser_get_url_stats)

    parser_get_url_stats.add_argument("url", type=unicode, help="url")

    parser_get_url_stats.set_defaults(func=get_url_stats)
    
    args = parser.parse_args()
    try:
        #fargs, fkwargs = config.func_args(args)
        result = args.func(**vars(args))
    except Exception, exc:
        print >> sys.stderr, "FATAL! %s executing %s" % (
            exc, args.func.func_name)
        return 1
    else:
        return result

if __name__ == '__main__':
    exit(main())

