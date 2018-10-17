import requests
import json
import time
import sys

def load_parametrs():  #чтение загрузочных параметров
    with open('loads.json', encoding='utf-8') as f:
        load_data = json.load(f)
    return load_data


class User:
    """ Класс для экземпляров описывающих пользователей VK и реализующий поиск групп,
        в которых состоит пользователь.
        Экземпляр класса создается на основе идентификатора пользователя VK"""

    def __init__(self, user_id):
        self.token = load_params['TOKEN']
        self.user_id = user_id

    def get_params(self):
        return {
            'access_token': self.token,
            'v': '5.85'
            }

    def get_requests(self, method, parametrs):  #выполнение запросов на сервер VK, получение ответов и обработка ошибок
        params = self.get_params()
        params.update(parametrs)
        activ = 0
        while True:
            response = requests.get(f'https://api.vk.com/method/{method}', params).json()
            print('.')
            if 'error' in response:
                if response['error']['error_code'] == 6:
                    time.sleep(0.8)
                    print('_')
                if response['error']['error_code'] == 18 or response['error']['error_code'] == 15:
                    return response['error']['error_msg']
            else:
                if method == 'groups.getById':
                    return response['response']
                else:
                    try:
                        return response['response'][0]
                    except KeyError:
                        return response['response']
                break

    def get_id(self):  #Получение ID пользователя по короткому имени (screen_name)
        params = dict()
        params['user_ids'] = self.user_id
        response = self.get_requests('users.get', params)
        self.user_id = int(response['id'])

    def get_info(self):  #Получение информации о пользователе
        params = dict()
        params['user_ids'] = self.user_id
        response = self.get_requests('users.get', params)
        user_name = response['first_name'] + ' ' + response['last_name']
        return user_name

    def friends_user(self):  #Формирование списка друзей
        params = dict()
        params['user_id'] = self.user_id
        friends = list()
        response = self.get_requests('friends.get', params)
        try:
            lst_friends = response['items']
            for friend in lst_friends:
                friends.append(User(friend))
            return friends
        except TypeError:
            return friends

    def groups_user(self):  #Формирование списка групп пользователя
        params = dict()
        params['user_id'] = self.user_id
        try:
            response = self.get_requests('groups.get', params)
            lst_groups = response['items']
            return lst_groups
        except TypeError:
            print(f'Пользователь ID{self.user_id}: {response}')
            return list()

    def get_group_info(self, groups_lst):  #Формирование словаря с описанием групп в токорых не состоит никто из друзей
        groups_info = list()
        params = dict()
        params['fields'] = 'members_count'
#        str_group = ''
        str_group = ','.join(map(str, groups_lst))
        params['group_ids'] = str_group
        response = self.get_requests('groups.getById', params)
        for i in response:
            group_info = dict()
            group_info = {'id': i['id'], 'name': i['name']}
            try:
                group_info['members_count'] = i['members_count']
            except KeyError:
                group_info['members_count'] = 'None'
            groups_info.append(group_info)
        return groups_info


def main_vk(name_or_id):  #функция поиска групп и друзей с выводом результата в файл 'groups.json'
    user = User(name_or_id)
    if name_or_id.isdigit() == False:  #Проверка указанных данных (id пользователя или короткое имя)
        user.get_id()
    user_name = user.get_info()
    print(user_name)
    groups = set(user.groups_user())
    print(f'Количество групп: {len(groups)}')
    friend_list = user.friends_user()
    print(f'Количество друзей: {len(friend_list)}')
    for friend in friend_list:
        groups_friend = list(friend.groups_user())
        if groups_friend:
            groups -= set(groups_friend)
    if groups:
        data = user.get_group_info(list(groups))
        with open('groups.json', 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

#Поиск ID в параметрах запуска
load_params = load_parametrs()
USER_ID = load_params['ID']
if len(sys.argv) > 1:
    USER_ID = sys.argv[1]
main_vk(USER_ID)
