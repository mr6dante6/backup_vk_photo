import json
from VK import VK


def get_social_network():
    while True:
        social_network = (input('Выберете социальную сеть '
                                '(пока что только VK):\n'
                                '1 - VK\n'))
        if social_network == '1':
            user_id = input('Введите id аккаунта: ')
            vk = VK(access_token, user_id)
            vk.check_accaunt()
            break
        else:
            print('Таких ещё нет, но мы работаем над пополнением списка.')


def save_json(photo):
    with open('photos.json', 'w') as f:
        json.dump(photo, f, sort_keys=True, indent=2)


if __name__ == '__main__':
    access_token = input('Введите токен vk:\n')
    get_social_network()
