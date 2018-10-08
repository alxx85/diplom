import requests
import json
import constants
import time


class User:
    """ Класс для экземпляров описывающих пользователей VK и реализующий поиск групп,
        в которых состоит пользователь.
        Экземпляр класса создается на основе идентификатора пользователя VK"""

    def __init__(self, user_id):
        self.token = constants.TOKEN
        self.user_id = user_id

    def get_params(self):
        return {
            'access_token': self.token,
            'v': '5.85'
            }

    def get_info(self):  #Получение информации о пользователе
        params = self.get_params()
        params['user_ids'] = self.user_id
        response = requests.get('https://api.vk.com/method/users.get', params).json()
        print(response['response'][0]['first_name'], response['response'][0]['last_name'])
        if response['response'][0]['id'] != self.user_id:
            self.user_id = int(response['response'][0]['id'])

    def friends_user(self):  #Формирование списка друзей
        params = self.get_params()
        params['user_id'] = self.user_id
        friends = list()
        response = requests.get('https://api.vk.com/method/friends.get', params).json()
        if 'response' in response:
            lst_friends = response['response']['items']
            if len(lst_friends) > 0:
                for friend in lst_friends:
                    friends.append(User(friend))
        return friends

    def groups_user(self):  #Формирование списка групп пользователя
        params = self.get_params()
        params['user_id'] = self.user_id
        try:
            response = requests.get('https://api.vk.com/method/groups.get', params).json()
            #    if 'response' in response:
            lst_groups = response['response']['items']
            return lst_groups
        except:
            print(f'Пользователь с ID{self.user_id} недоступен...')
            return list()

    def get_group_info(self, groups_lst):  #Формирование словаря с описанием групп в токорых не состоит никто из друзей
        group_info = list()
        params = self.get_params()
        params['fields'] = 'members_count'
        for group_id in groups_lst:
            params['group_ids'] = group_id
            response = requests.get('https://api.vk.com/method/groups.getById', params).json()
            if 'response' in response:
                group_inf = dict()
                group_inf['id'] = response['response'][0]['id']
                group_inf['name'] = response['response'][0]['name']
                group_inf['members_count'] = response['response'][0]['members_count']
                group_info.append(group_inf)
        return group_info


def get_requests(max_quantity = 1, current_numb = 1):  #Отображение выполняемого запроса и общее их колличество
    print(f'Выполняется запрос №{current_numb} из {max_quantity}.')
    if current_numb >= max_quantity:
        current_numb = 0
    time.sleep(0.34)
    current_numb += 1

#friends_dict = dict()
numb_request = 1
user1 = User(constants.USER_ID)
get_requests()
user1.get_info()
get_requests()
groups = set(user1.groups_user())
print('Колличество групп: ', len(groups))
get_requests()
friend_list = user1.friends_user()
print('Колличество друзей: ', len(friend_list))
numb_request = 1
for friend in friend_list:
    get_requests(len(friend_list), numb_request)
    groups_friend = list(friend.groups_user())
    if len(groups_friend) != 0:
        #friends_dict[friend] = groups_friend
        groups -= set(groups_friend)
    numb_request += 1
if len(groups) > 0:
    data = user1.get_group_info(groups)
with open('groups.json', 'w', encoding = 'utf8') as f:
    json.dump(data, f, ensure_ascii = False, indent = 4)
