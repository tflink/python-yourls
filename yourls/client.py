# client.py
#  - Python client for yourls
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
# Original Author:
#       Tim Flink <tflink@redhat.com>
# Updates:
#       Setu Shah

"""
.. module:: yourls.client
   :synopsis: A simple Python client for the YOURLS URL shortener.
"""

import urllib
try:
    # Python 3
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
    from urllib.error import URLError
except ImportError:
    # Python 2
    from urllib import urlencode
    from urllib2 import urlopen, Request, URLError
import json
from yourls import YourlsError, YourlsOperationError

class YourlsClient():

    def __init__(self, apiurl, username=None, password=None, token=None, output_format='json'):
        """The use of a username/password combo or a signature token is required

        :param apiurl: The location of the api php file
        :param username: The username to login with (not needed with signature token)
        :param password: The password to login with (not needed with signature token)
        :param token: The signature token to use (not needed with username/password combo)
        :param output_format: The format in which the API output should be requested. Possible options are `json`, `jsonp`, `xml` or `simple`
        :throws: YourlsError for incorrent parameters

        """
        if output_format not in ['json', 'jsonp', 'xml', 'simple']:
            raise YourlsError("Type of output requested unavailable")


        self.data_format = output_format

        if not apiurl:
            raise YourlsError("An API URL is required")
        self.apiurl = apiurl

        if not username or not password:
            if not token:
                raise YourlsError("Username and Password or signature token are required")
            else:
                self.signature = token
                self.std_args = {'signature': token, 'format': self.data_format}

        else:
            self.username = username
            self.password = password
            self.std_args = {'username':self.username, 'password':self.password,
                             'format':self.data_format}


    def _send_request(self, args):
        """Encapsulates the actual sending of a request to a YOURLS instance

        :param args: The arguments to send to YOURLS

        """
        urlargs = urlencode(self._make_args(args))
        req = Request(self.apiurl)
        try:
            req.data = urlargs.encode('utf-8')
            req.headers ={'User-Agent': 'Mozilla 5.0'}
        except Exception as e:
            req.add_data(urlargs)
        r = urlopen(req)
        data = r.read()
        return data


    def _make_args(self, new_args):
        """Convenience method for putting args into the proper format

        :param new_args: Dictionary containing the args to pass on

        """
        args = self.std_args.copy()
        args.update(new_args)
        return args


    def _base_request(self, args, url=None):
        """Encapsulates common code and error handling for the access methods

        :param args: The arguments to send to YOURLS
        :param url: The url (short or long) arg being used in the request
        :raises: YourlsOperationError

        """
        try:
            data = json.loads(self._send_request(args))
        except URLError as error:
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
        :returns: str, str -- The short URL, the title of the original webpage
        :raises: YourlsOperationError

        """
        args = {'action':'shorturl', 'url': url, 'format': self.data_format}

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

        return raw_data['shorturl'], raw_data['title']


    def expand(self, shorturl):
        """Expand a shortened URL to its original form

        :param shorturl: The URL to expand
        :returns: str -- The expanded URL
        :raises: YourlsOperationError

        """
        args = {'action' : 'expand', 'shorturl' : shorturl, 'format' : self.data_format}

        raw_data = self._base_request(args, shorturl)

        if not 'longurl' in raw_data:
            raise YourlsOperationError(shorturl, raw_data['message'])

        return raw_data['longurl']


    def url_stats(self, shorturl):
        """Get statistics about a shortened URL

        :param shorturl: The URL to expand
        :returns: dict -- Stats for the short-link passed
        :raises: YourlsOperationError

        """

        args = {'action' : 'url-stats', 'shorturl' : shorturl, 'format' : self.data_format}

        raw_data = self._base_request(args, shorturl)

        if raw_data['statusCode'] != 200:
            raise YourlsOperationError(shorturl, raw_data['message'])

        return raw_data['link']


    def stats(self, filter, limit=10):
        """Get link-wise statistics.

        :param filter: The filter for requesting stats on links, options: `top`, `bottom`, `rand` or `last`
        :param limit: The maximum number of links to request
        :returns: (list, dict) -- A list containing stats for all filtered links, a dict containing overall stats
        :raises: YourlsOperationError

        """
        if filter in ['top', 'bottom', 'rand', 'last']:
            args = {'action': 'stats', 'filter': filter, 'format' : self.data_format}
            if limit:
                args['limit'] = limit
        else:
            raise YourlsError('filter incorrect')

        raw_data = self._base_request(args)

        if raw_data['statusCode'] != 200:
            raise YourlsOperationError(filter, raw_data['message'])

        return raw_data['links'], raw_data['stats']


    def db_stats(self):
        """Get statistics about all links.

        :returns: a dict containing `total_links` and `total_clicks`
        :raises: YourlsOperationError

        """
        args = {'action': 'db-stats', 'format' : self.data_format}

        raw_data = self._base_request(args)

        if raw_data['statusCode'] != 200:
            raise YourlsOperationError(filter, raw_data['message'])

        return raw_data['db-stats']


