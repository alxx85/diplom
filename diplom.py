import requests
import json
import time
import sys

def load_params(parametr):  #чтение загрузочных параметров
    with open('loads.json', encoding='utf-8') as f:
        load_data = json.load(f)
    return load_data[parametr]


class User:
    """ Класс для экземпляров описывающих пользователей VK и реализующий поиск групп,
        в которых состоит пользователь.
        Экземпляр класса создается на основе идентификатора пользователя VK"""

    def __init__(self, user_id):
        self.token = load_params('TOKEN')
        self.user_id = user_id

    def get_params(self):
        return {
            'access_token': self.token,
            'v': '5.85'
            }

    def get_requests(self, request, parametrs):  #выполнение запросов на сервер VK, получение ответов и обработка ошибок
        response = requests.get(f'https://api.vk.com/method/{request}', parametrs)
        print('.')
        if 'error' in response.text:
            if response.json()['error']['error_msg'] == 'Too many requests per second':
                time.sleep(0.8)
                print('_')
                response = requests.get(f'https://api.vk.com/method/{request}', parametrs)
            else:
                return response.json()['error']['error_msg']

        if 'deactivated' not in response.text:
            return response.json()['response']
        else:
            if request == 'users.get':
                print(f'Статус пользователя: {response.json()["response"][0]["deactivated"]}!')
                exit()
            else:
                return response.json()['response']

    def get_info(self):  #Получение информации о пользователе
        params = self.get_params()
        params['user_ids'] = self.user_id
        response = self.get_requests('users.get', params)
        if response[0]['id'] != self.user_id:
            self.user_id = int(response[0]['id'])
        user_name = response[0]['first_name'] + ' ' + response[0]['last_name']
        return user_name

    def friends_user(self):  #Формирование списка друзей
        params = self.get_params()
        params['user_id'] = self.user_id
        friends = list()
        response = self.get_requests('friends.get', params)
        lst_friends = response['items']
        for friend in lst_friends:
            friends.append(User(friend))
        return friends

    def groups_user(self):  #Формирование списка групп пользователя
        params = self.get_params()
        params['user_id'] = self.user_id
        try:
            response = self.get_requests('groups.get', params)
            lst_groups = response['items']
            return lst_groups
        except (KeyError, TypeError):
            print(f'Пользователь ID{self.user_id}: {response}')
            return list()

    def get_group_info(self, groups_lst):  #Формирование словаря с описанием групп в токорых не состоит никто из друзей
        groups_info = list()
        params = self.get_params()
        params['fields'] = 'members_count'
        str_group = ''
        for group_id in groups_lst:
            str_group += str(group_id) + ','
        params['group_ids'] = str_group
        response = self.get_requests('groups.getById', params)
        for i in response:
            group_info = dict()
            group_info['id'] = i['id']
            group_info['name'] = i['name']
            try:
                group_info['members_count'] = i['members_count']
            except KeyError:
                group_info['members_count'] = 'None'
            groups_info.append(group_info)
        return groups_info


def main_vk(user):  #функция поиска групп и друзей с выводом результата в файл 'groups.json'
    user_name = user.get_info()
    print(user_name)
    groups = set(user.groups_user())
    print('Количество групп: ', len(groups))
    friend_list = user.friends_user()
    print('Количество друзей: ', len(friend_list))
    for friend in friend_list:
        groups_friend = list(friend.groups_user())
        if len(groups_friend) != 0:
            groups -= set(groups_friend)
    if len(groups) > 0:
        data = user.get_group_info(groups)
        with open('groups.json', 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

#Поиск ID в параметрах запуска
USER_ID = load_params('ID')
if len(sys.argv) > 1:
    USER_ID = sys.argv[1]
user = User(USER_ID)
main_vk(user)
