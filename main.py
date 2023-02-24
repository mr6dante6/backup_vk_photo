import json

import requests
import time
import datetime
from progress.bar import IncrementalBar
import YANDEX_UPLOADER as ya


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

    def get_albums(self):
        url = 'https://api.vk.com/method/photos.getAlbums'
        params = {'owner_id': self.id, 'need_system': 1}
        response = requests.get(url, params={**self.params, **params}).json()
        count = 1
        for i in response['response']['items']:
            self.album_dict.update({f"{count}": {"id": i['id'], "title": i["title"], 'count_photo': i["size"]}})
            print(f'{count} - {i["title"]} - {i["size"]} фото.')
            count += 1

        while True:
            change_album = input('Введите номер альбома: ')
            if change_album in self.album_dict:
                self.get_photo(self.album_dict[change_album])
                ya_uploader = ya.YaUploader(input('Введите токен:\n'))
                ya_uploader.create_folder(self.album_dict[change_album]['title'])
                ya_uploader.upload_photo(self.album_dict[change_album]['title'], self.photo, self.url_photo)
                break
            else:
                print('Такого альбома не существует!')

    def get_photo(self, album_dict):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id, 'album_id': f'{album_dict["id"]}', 'count': 100, 'extended': 1}
        params.update({'offset': self.offset})
        bar = IncrementalBar('Получение информации о фотографиях: ', max=album_dict['count_photo'])

        while True:
            response = requests.get(url, params={**self.params, **params}).json()
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
            for type in char_photo['sizes']:
                if i == type['type']:
                    return {'date': char_photo['date'], 'likes': char_photo['likes']['count'], 'size': type['type'],
                            'photo_url': type['url']}

    def get_file_name(self):
        for items in self.url_photo:
            if items['likes'] in self.unical_likes:
                self.photo.append({'file_name': f"{items['likes']}.jpg", 'size': items['size']})
            else:
                date_create = datetime.datetime.fromtimestamp(items['date']).strftime('%Y-%m-%d %H-%M-%S')
                self.photo.append({
                    'file_name': f"{items['likes']} ({date_create}).jpg",
                    'size': items['size']})
        with open('photos.json', 'w') as f:
            json.dump(self.photo, f, sort_keys=True, indent=2)


access_token = 'vk1.a.r5BoLgT4oXNVMrgTAXmJRJl5i3utRP-EJHu5QdXeW2r' \
               'XM-QgfL459PoQqdNSy4bJCfeOEFolYhf1TzugkrKgPtvYhKC-' \
               '1oygBSKKoggN-UCGAcDIwhYNsTRij12vuvZjaCm-K8vI60clP' \
               'yyL1-794BiXJcxs2VCbIr0O0PZaOSRxtACq_gYT3iwxW5Axm_' \
               'GwWYQZGUZmT0yzvhMK7P1MHg'

if __name__ == '__main__':
    user_id = input('Введите id аккаунта: ')
    vk = VK(access_token, user_id)
    vk.get_albums()
