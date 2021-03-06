#! /usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Etienne Chové <chove@crans.org> 2009                       ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
##                                                                       ##
###########################################################################

from bottle import route, redirect, response, html_escape
from modules import utils
from modules.utils import i10n_select_auto
from modules import query
from lxml import etree
from lxml.builder import E, ElementMaker

from api.user_utils import _user, _user_count
from .issues import rss, gpx, kml


@route('/byuser')
def byUser():
    redirect("byuser/")


@route('/byuser/<username>.<format:ext>')
def user(db, lang, username=None, format=None):
    params, username, errors = _user(db, lang, username)

    for error in errors:
        error["subtitle"] = i10n_select_auto(error["subtitle"], lang)
        error["title"] = i10n_select_auto(error["title"], lang)
        error["menu"] = i10n_select_auto(error["menu"], lang)

    if format == 'rss':
        response.content_type = 'application/rss+xml'
        xml = rss(website=utils.website, lang=lang[0], params=params, query='users={0}'.format(username), main_website=utils.main_website, remote_url_read=utils.remote_url_read, issues=errors)
        return etree.tostring(xml, pretty_print=True)
    elif format == 'gpx':
        response.content_type = 'application/gpx+xml'
        xml = gpx(website=utils.website, lang=lang[0], params=params, query='users={0}'.format(username), main_website=utils.main_website, remote_url_read=utils.remote_url_read, issues=errors)
        return etree.tostring(xml, pretty_print=True)
    elif format == 'kml':
        response.content_type = 'application/vnd.google-earth.kml+xml'
        xml = kml(website=utils.website, lang=lang[0], params=params, query='users={0}'.format(username), main_website=utils.main_website, remote_url_read=utils.remote_url_read, issues=errors)
        return etree.tostring(xml, pretty_print=True)
    else:
        count = len(errors)
        for error in errors:
            error['timestamp'] = str(error['timestamp'])
        return dict(username=username, users=params.users, count=count, errors=list(map(dict, errors)), website=utils.website + '/' + lang[0], main_website=utils.main_website, remote_url_read=utils.remote_url_read)


@route('/byuser_count/<username>.rss')
def user_count(db, lang, username=None):
    count = _user_count(db, username)
    print(count)
    response.content_type = "application/rss+xml"
    xml = E.rss(
        E.channel(
            E.title('Osmose - ' + username),
            E.description(_("Statistics for user {0}").format(username)),
            E.link('http://{}/byuser/{}'.format(utils.website, username)),
            E.item(
                E.title(_("Number of level {level} issues: {count}").format(level=1, count=count[1]))
            ),
            E.item(
                E.title(_("Number of level {level} issues: {count}").format(level=2, count=count[2]))
            ),
            E.item(
                E.title(_("Number of level {level} issues: {count}").format(level=3, count=count[3]))
            ),
        ),
        version = '2.0',
    )
    return etree.tostring(xml, pretty_print=True)


@route('/byuser_count/<username>')
def user_count(db, lang, username=None):
    return _user_count(db, username)
