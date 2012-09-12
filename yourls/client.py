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

from yourls import __version__, YourlsError, YourlsOperationError

LIMIT=100

class YourlsClient():

    def __init__(self, apiurl, username=None, 
                password=None, token=None, format='json'):
        """The use of a username/password combo or a signature token is required

        :param apiurl: The location of the api php file
        :param username: The username to login with (not needed with signature token)
        :param password: The password to login with (not needed with signature token)
        :param token: The signature token to use (not needed with username/password combo)
        :param format: The default format for all messages
        
        :throws: YourlsError for incorrent parameters

        """
        self.data_format = format

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


    def shorturl(self, url, keyword=None, title=None):
        """Request a shortened URL from YOURLS with an optional keyword request

        :param url: The URL to shorten
        :type url: str
        :param keyword: The keyword keyword to request
        :type keyword: str
        :param title: Use the given title instead of download it from the URL, this will increase performances
        :type title: str
        :returns: str -- The short URL
        :raises: YourlsOperationError

        """
        args = {'action':'shorturl', 'url':url}

        if keyword:
            args['keyword'] = keyword

        if keyword:
            args['title'] = keyword

        # shorten
        raw_data = self._base_request(args, url)

        # parse result
        if raw_data['status'] == 'fail' and raw_data['code'] == 'error:keyword':
            raise YourlsOperationError(url, raw_data['message'])

        if not 'shorturl' in raw_data:
            raise YourlsOperationError(url, 'Unknown error: %s' % raw_data['message'])

        return raw_data['shorturl']

    shorten = shorturl

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


    def url_stats(self, shorturl):
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
    get_url_stats = url_stats

    def stats(self, filter, limit=LIMIT):
        """Get statistics about your links

        :param filter: either "top", "bottom", "rand" or "last"
        :type filter: str
        :param limit: maximum number of links to return
        :type limit: int
        :returns: a list of stuff - FIXME, this isn't complete
        :raises: YourlsOperationError

        """

        args = {'action' : 'stats', 'filter' : filter, 
                'limit':limit, 'format' : 'json'}

        raw_data = self._base_request(args, shorturl)

        if raw_data['statusCode'] != 200:
            raise YourlsOperationError(shorturl, raw_data['message'])

        return raw_data["stats"]

    def db_stats(self):
        """Get global link and click count

        :returns: a list of stuff - FIXME, this isn't complete
        :raises: YourlsOperationError

        """

        args = {'action' : 'db-stats', 'format' : 'json'}
        raw_data = self._base_request(args, shorturl)
        return raw_data

def get_server(apiurl, **kwargs):
    kw = dict(apiurl=apiurl)
    for key in ["username", "password", "token"]:
        value = kwargs.get(key, None)
        if value:
            kw[key] = value
    return YourlsClient(**kw)

def shorturl(url, keyword, title=None, server=None, **kwargs):
    if server is None:
        server = get_server(**kwargs)
    return server.shorturl(url, keyword=keyword, title=title)
shorten = shorturl

def expand(shorturl, server=None, **kwargs):
    if server is None:
        server = get_server(**kwargs)
    return server.expand(shorturl)

def url_stats(shorturl, server=None, **kwargs):
    if server is None:
        server = get_server(**kwargs)
    return server.url_stats(shorturl)
get_url_stats = url_stats

def stats(filter="top", limit=LIMIT, server=None, **kwargs):
    if server is None:
        server = get_server(**kwargs)
    return server.stats(filter, limit)

def db_stats(server=None, **kwargs):
    if server is None:
        server = get_server(**kwargs)
    return server.db_stats()

def set_yourls_parser(parser):
    parser.add_argument("-s", "--apiurl", metavar="uri",
        default="http://localhost/yourls/yourls-api.php",
        help="Yourls API URL. default=%(default)s")
    parser.add_argument("-T", "--token", help="Token")
    parser.add_argument("-u", "--username", help="Username")
    parser.add_argument("-p", "--password", help="Password")

def main():
    """Yourls command line access"""
    
    import argparse

    parser = argparse.ArgumentParser(
        description='Yourls Client',
        version="%(prog)s " + __version__
        )

    subparsers = parser.add_subparsers(dest="command")

    #
    #shorturl command
    parser_shorturl = subparsers.add_parser('shorturl', 
        help="get short URL for a link")

    set_yourls_parser(parser_shorturl)
    parser_shorturl.add_argument("-k", "--keyword", type=unicode, 
        help="optional keyword for custom short URLs")
    parser_shorturl.add_argument("-t", "--title", type=unicode, 
        help="title")
    parser_shorturl.add_argument("url", type=unicode, 
        help="the url to shorten")
    parser_shorturl.set_defaults(func=shorturl)

    #expand command
    parser_expand = subparsers.add_parser('expand', help="get long URL of a shorturl")
    set_yourls_parser(parser_expand)
    parser_expand.add_argument("url", type=unicode, 
        help="the shorturl to expand (can be either 'abc' or 'http://site/abc')")
    parser_expand.set_defaults(func=expand)

    #url_stats command
    parser_url_stats = subparsers.add_parser(
        'url-stats', help="get stats about one short URL")
    set_yourls_parser(parser_url_stats)
    parser_url_stats.add_argument("shorturl", type=unicode, 
        help="the shorturl for which to get stats (can be either 'abc' or 'http://site/abc')")
    parser_url_stats.set_defaults(func=url_stats)

    #stats command
    parser_stats = subparsers.add_parser(
        'stats', help="get stats about your links")
    set_yourls_parser(parser_stats)
    parser_stats.add_argument("-l","--limit", type=int, default=LIMIT,
        help="maximum number of links to return. default=%(default)s")
    parser_stats.add_argument("-f", "--filter", type=str, default="top",
        choices=['top', 'bottom', 'rand', 'last'],
        help="the filter: either 'top', 'bottom' , 'rand' or 'last'. default=%(default)s")
    parser_stats.set_defaults(func=stats)
    
    #db_stats command
    parser_db_stats = subparsers.add_parser(
        'db-stats', help="get global link and click count")
    set_yourls_parser(parser_db_stats)
    parser_db_stats.set_defaults(func=db_stats)

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

