# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcplugin

import json
import routing

plugin = routing.Plugin()


@plugin.route('/')
def index():
    item_one = xbmcgui.ListItem("Test Item One")
    item_one.setProperty("id", "one")
    item_two = xbmcgui.ListItem("Test Item Two")
    item_two.setProperty("id", "two")
    item_three = xbmcgui.ListItem("Test Item Three")
    item_three.setProperty("id", "three")
    
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(
        show_category, "one"), item_one, True)
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(
        show_category, "two"), item_two, True)
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(
        show_category, "three"), item_three, True)
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(make_json_call),
                     xbmcgui.ListItem("Test JSON Call"), False)
    xbmcplugin.endOfDirectory(plugin.handle)
    
    for item in [item_one, item_two, item_three]:
        xbmc.log('{} - ListItem.Property(id) = {}'.format(item.getLabel(),
                                                          item.getProperty('id')),
                 xbmc.LOGNOTICE)


@plugin.route('/test/json')
def make_json_call():
    params = {'jsonrpc': '2.0', 'method': 'Files.GetDirectory',
              'params': {'properties': ['title', 'file'],
                         'directory': 'plugin://plugin.program.example/'},
              'id': 1}

    data = json.dumps(params)
    request = xbmc.executeJSONRPC(data)

    try:
        response = json.loads(request)
    except UnicodeDecodeError:
        response = json.loads(request.decode('utf-8', 'ignore'))

    try:
        if 'result' in response:
            response = response['result']
    except KeyError:
        return None

    dumped = json.dumps(response)
    xbmc.log(dumped, xbmc.LOGNOTICE)
    xbmcgui.Dialog().notification('Test', '{} items returned in response.'
                                          .format(len(response['files'])))


@plugin.route('/category/<category_id>')
def show_category(category_id):
    xbmcplugin.addDirectoryItem(plugin.handle, "",
        xbmcgui.ListItem("Hello test {}!".format(category_id)))
    xbmcplugin.endOfDirectory(plugin.handle)

def run():
    plugin.run()
