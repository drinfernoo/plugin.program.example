# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

import contextlib
import json
import routing
import time

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')

plugin = routing.Plugin()


@plugin.route('/')
def index_menu():
    with timing("Loading Root Menu"):
        index()


@plugin.route('/category/<category_id>')
def show_category(category_id):
    xbmcplugin.addDirectoryItem(plugin.handle, "",
        xbmcgui.ListItem("Hello test {}!".format(category_id)))
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/test/json')
def test_json_menu():
    with timing("Testing JSON Response"):
        test_json_call()


@plugin.route('/test/window')
def test_mock_menu():
    with timing("Testing Mock Window"):
        test_mock_window()


def index():
    item_one = xbmcgui.ListItem("Test Item One")
    item_two = xbmcgui.ListItem("Test Item Two")
    item_three = xbmcgui.ListItem("Test Item Three")
    item_json = xbmcgui.ListItem("Test JSON Call")
    item_window = xbmcgui.ListItem("Test Mock Window")  # pointing multiple widgets here freezes Kodi :D

    item_one.setProperty("my_property", "one")
    item_two.setProperty("my_property", "two")
    item_three.setProperty("my_property", "three")

    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(
        show_category, "one"), item_one, True)
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(
        show_category, "two"), item_two, True)
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(
        show_category, "three"), item_three, True)

    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(test_json_menu),
        item_json, True)
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(test_mock_menu),
        item_window, True)

    for item in [item_one, item_two, item_three, item_json, item_window]:
        xbmc.log('{}.getProperty("my_property") = {}'
                     .format(item, item.getProperty('my_property')),
                 xbmc.LOGDEBUG)

    xbmcplugin.endOfDirectory(plugin.handle)


def test_json_call():
    params = {'jsonrpc': '2.0', 'method': 'Files.GetDirectory',
              'params': {'properties': ['title'],
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
    xbmcplugin.addDirectoryItem(plugin.handle, '',
        xbmcgui.ListItem('{} items returned in response.'.format(len(
                                                                 response.get(
                                                                    'files')))),
                         False)
    xbmcplugin.endOfDirectory(plugin.handle)


def test_mock_window():
    content = plugin.url_for(index_menu)
    items = []

    class MockWindow(xbmcgui.WindowXMLDialog):

        def __init__(self, *args, **kwargs):
            xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
            self.content = kwargs['content']

        def onInit(self):
            xbmcgui.WindowXMLDialog.onInit(self)
            self.load_content(self.content)

        def load_content(self, path):
            num = xbmc.getInfoLabel('Container(1000).NumItems')
            if num:
                num = int(num)

            self.setProperty('dir_content', path)
            while not num or not num > 0:
                num = int(xbmc.getInfoLabel('Container(1000).NumItems'))
            
            # this code never gets reached by any menu, if there are multiple
            # widgets pointed here, because the windows get "confused"?
            xbmc.log('Container(1000).NumItems = {}'.format(num), xbmc.LOGNOTICE)

            for i in range(num):
                label = ('Container(1000).ListItem({})'
                         '.Property(my_property)').format(i)
                value = xbmc.getInfoLabel(label)
                xbmcplugin.addDirectoryItem(plugin.handle, '',
                    xbmcgui.ListItem('my_property = {}'.format(value)), False)

            self.clearProperty('dir_content')
            self.close()

    test = MockWindow('mock_window.xml', ADDON_PATH, 'Default', content=content)
    test.doModal()

    del test
    xbmcplugin.endOfDirectory(plugin.handle)


@contextlib.contextmanager
def timing(description):
    start = time.time()
    yield
    elapsed = time.time() - start

    xbmc.log("{}: {}".format(description, elapsed), xbmc.LOGNOTICE)


def run():
    plugin.run()
