import requests
import time
import datetime
from progress.bar import IncrementalBar
import YANDEX_UPLOADER as YA
import __main__


class VK:

    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}
        self.photo_list = []
        self.sizes_photo = ['w', 'z', 'y', 'r', 'q', 'p', 'o', 'x', 'm', 's']
        self.url_photo = []
        self.offset = 0
        self.unical_likes = []
        self.photo = []
        self.album_dict = {}

    def check_accaunt(self):
        while True:
            url = 'https://api.vk.com/method/users.get'
            params = {'user_id': self.id}
            response = requests.get(url, params={**self.params, **params}).json()
            response2 = response["response"][0]['can_access_closed']
            print(response2)
            if not response2:
                self.id = input('Введён ID закрытого аккаунта, введите другой ID:\n')
            elif response2:
                self.get_albums()
                break
            else:
                self.id = input('Пользователь не найден, введите другой ID:\n')

    def get_albums(self):
        url = 'https://api.vk.com/method/photos.getAlbums'
        params = {'owner_id': self.id, 'need_system': 1}
        while True:
            response = requests.get(url, params={**self.params, **params})
            if 200 <= response.status_code <= 299:
                print(response.status_code)
                break
            time.sleep(.5)
        response = response.json()
        count = 1

        for i in response['response']['items']:
            self.album_dict.update({f"{count}": {"id": i['id'], "title": i["title"], 'count_photo': i["size"]}})
            print(f'{count} - {i["title"]} - {i["size"]} фото.')
            count += 1

        while True:
            change_album = input('Введите номер альбома: ')
            if change_album in self.album_dict:
                self.get_photo(self.album_dict[change_album])
                __main__.save_json(self.photo)
                ya_uploader = YA.YaUploader(input('Введите токен:\n'))
                ya_uploader.set_folder_name(self.album_dict[change_album]['title'])
                ya_uploader.upload_photo(self.photo, self.url_photo)
                break
            else:
                print('Такого альбома не существует!')

    def get_photo(self, album_dict):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id, 'album_id': f'{album_dict["id"]}', 'count': 100, 'extended': 1}
        params.update({'offset': self.offset})
        bar = IncrementalBar('Получение информации о фотографиях: ', max=album_dict['count_photo'])

        while True:
            while True:
                response = requests.get(url, params={**self.params, **params})
                if 200 <= response.status_code <= 299:
                    print(response.status_code)
                    break
            response = response.json()
            params['offset'] += 100
            if response['response']['items']:
                for i in response['response']['items']:
                    self.photo_list.append(i)
                    bar.next()
            else:
                bar.finish()
                break
            time.sleep(0.25)

        for items in self.photo_list:
            self.unical_likes.append(items['likes']['count'])
            self.url_photo.append(self.get_max_size(items))

        self.unical_likes = [e for e in set(self.unical_likes) if self.unical_likes.count(e) == 1]

        self.get_file_name()

    def get_max_size(self, char_photo):
        for i in self.sizes_photo:
            for type_size in char_photo['sizes']:
                if i == type_size['type']:
                    return {'date': char_photo['date'],
                            'likes': char_photo['likes']['count'],
                            'size': type_size['type'],
                            'photo_url': type_size['url']
                            }

    def get_file_name(self):
        for items in self.url_photo:
            if items['likes'] in self.unical_likes:
                self.photo.append({'file_name': f"{items['likes']}.jpg", 'size': items['size']})
            else:
                date_create = datetime.datetime.fromtimestamp(items['date']).strftime('%Y-%m-%d %H-%M-%S')
                self.photo.append({
                    'file_name': f"{items['likes']} ({date_create}).jpg",
                    'size': items['size']})
