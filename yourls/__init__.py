# yourls
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

__version__ = "0.2.0"

class YourlsError(Exception):
    '''Base exception for all Yourls exceptions'''
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

class YourlsOperationError(YourlsError):
    '''Error during URL operations'''
    def __init__(self, url, message):
        self.url = url
        self.message = message
    def __str__(self):
        return repr('Error with url \'%s\' - %s' % (self.url, self.message))

