import requests
import json
import constants
import time


class User:
    """ Класс для экземпляров описывающих пользователей VK и реализующий поиск групп,
        в которых состоит пользователь, но не состоит никто из его друзей
        Экземпляр класса создается на основе идентификатора пользователя VK"""

    def __init__(self, user_id):
        self.token = constants.TOKEN
        self.user_id = user_id

    def __str__(self):
        return str(self.get_info())

    def get_params(self):
        return {
            'access_token': self.token,
            'v': '5.85'
            }

    def get_requests(self):
        print('.')
        time.sleep(0.4)

    def get_info(self):
        params = self.get_params()
        params['user_ids'] = self.user_id
        self.get_requests()
        response = requests.get('https://api.vk.com/method/users.get', params).json()
        print(response['response'][0]['first_name'], response['response'][0]['last_name'])
        if response['response'][0]['id'] != self.user_id:
            self.user_id = int(response['response'][0]['id'])

    def friends_user(self):
        params = self.get_params()
        params['user_id'] = self.user_id
        friends = list()
        self.get_requests()
        response = requests.get('https://api.vk.com/method/friends.get', params).json()
        if 'response' in response:
            lst_friends = response['response']['items']
            if len(lst_friends) > 0:
                for friend in lst_friends:
                    friends.append(User(friend))
        return friends

    def groups_user(self):
        params = self.get_params()
        params['user_id'] = self.user_id
        self.get_requests()
        response = requests.get('https://api.vk.com/method/groups.get', params).json()
        if 'response' in response:
            lst_groups = response['response']['items']
        return lst_groups

    def groups_none_friends(self, list_groups):
        params = self.get_params()
        params['filter'] = 'friends'
        list_groups_none_friends = list()
        for group in list_groups:
            params['group_id'] = group
            self.get_requests()
            response = requests.get('https://api.vk.com/method/groups.getMembers', params).json()
            if 'response' in response:
                if response['response']['count'] == 0:
                    list_groups_none_friends.append(group)
        return list_groups_none_friends

    def get_group_info(self, groups_lst):
        group_info = list()
        params = self.get_params()
        params['fields'] = 'members_count'
        for group_id in groups_lst:
            params['group_ids'] = group_id
            self.get_requests()
            response = requests.get('https://api.vk.com/method/groups.getById', params).json()
            if 'response' in response:
                group_inf = dict()
                group_inf['id'] = response['response'][0]['id']
                group_inf['name'] = response['response'][0]['name']
                group_inf['members_count'] = response['response'][0]['members_count']
                group_info.append(group_inf)
        return group_info


user1 = User(constants.USER_ID)
user1.get_info()
#friend_list = user1.friends_user()
#print('Колличество друзей: ', len(friend_list))
groups_list = user1.groups_user()
groups = user1.groups_none_friends(groups_list)
if len(groups) > 0:
    data = user1.get_group_info(groups)
with open('groups.json', 'w', encoding = 'utf8') as f:
    json.dump(data, f, ensure_ascii = False, indent = 4)