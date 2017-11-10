import os
import sys
import time
import vkplus as vkb
import settings


def main():
    path = 'plugins/'
    cmds = {}
    plugins = {}

    global lastmessid
    lastmessid = 0

    print('Vk_Bot by Adventurous Community')

    print('Авторизация...')

    vk = vkb.VkPlus(settings.token)

    print('---------------------------')

    # Подгружаем плагины
    sys.path.insert(0, path)
    for f in os.listdir(path):
        fname, ext = os.path.splitext(f)
        if ext == '.py':
            mod = __import__(fname)
            plugins[fname] = mod.Plugin(vk)
    sys.path.pop(0)

    print('---------------------------')

    for plugin in plugins.values():
        for key, value in plugin.getkeys().items():
            cmds[key] = value

    print('Приступаю к приему сообщений')

    while True:

        values = {
            'out': 0,
            'offset': 0,
            'count': 20,
            'time_offset': 50,
            'filters': 0,
            'preview_length': 0,
            'last_message_id': lastmessid
        }

        response = vk.api.method('messages.get', values)
        if response['items']:
            lastmessid = response['items'][0]['id']
            for item in response['items']:
                print('> ' + item['body'])
                command( item, cmds)
                vk.markasread(item['id'])  # Помечаем прочитанным

        time.sleep(0.5)


def command(message, cmds):
    if message['body'] == u'':
        return
    words = message['body'].lower().split()
    if words[0][0] == '/':
        if len(words) >= 1 and words[0][1:] in cmds:
            cmds[words[0][1:].lower()].call(message)


if __name__ == '__main__':
    main()