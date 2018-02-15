import vk_api


def captcha_handler(captcha):
    key = input("Enter Captcha {0}: ".format(captcha.get_url())).strip()
    return captcha.try_again(key)

def url2vk_id(url):
    url = url.split('/')[-1]
    boom = vk_api.VkApi()
    result = boom.method('users.get', {'user_ids':url})
    return result[0]['id']

class VkPlus:
    api = None
    def __init__(self, token):
        try:
            self.api = vk_api.VkApi(token=token)
            self.api._auth_token()
        except vk_api.AuthorizationError as error_msg:
            print(error_msg)
            return None


    def addUser(self, user_id):
        self.api.method('friends.add', {'user_id':user_id})


    def respond(self, to, values):
        if 'chat_id' in to:
            values['chat_id'] = to['chat_id']
            self.api.method('messages.send', values)

        else:
            values['user_id'] = to['user_id']
            self.api.method('messages.send', values)

    def send(self, **kwargs):
        self.api.method('messages.send', kwargs)


    def markasread(self, id):
        values = {
            'message_ids': id
        }
        self.api.method('messages.markAsRead', values)
