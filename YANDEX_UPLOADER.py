import requests
import time
from progress.bar import IncrementalBar


class YaUploader:
    host = 'https://cloud-api.yandex.net/'

    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.token}'}

    def create_folder(self, fol_name: str):
        url = self.host + 'v1/disk/resources'
        params = {'path': f'/{fol_name}'}
        requests.put(url, headers=self.get_headers(), params=params)

    def upload_photo(self, fol_name, file_name, file_url):
        url_upload = self.host + 'v1/disk/resources/upload'
        count = 0
        bar = IncrementalBar('Копирование фотографий: ', max=len(file_name))
        while count < len(file_name):
            params = {'path': f'/{fol_name}/{file_name[count]["file_name"]}', 'url': f'{file_url[count]["photo_url"]}'}
            requests.post(url_upload, headers=self.get_headers(), params=params)
            count += 1
            bar.next()
            time.sleep(.5)
        bar.finish()
        self.upload(fol_name)

    def get_upload_link(self, fol_name):
        url = self.host + 'v1/disk/resources/upload/'
        params = {'path': f'/{fol_name}/photos.json'}
        response = requests.get(url, headers=self.get_headers(), params=params)
        return response.json()['href']

    def upload(self, fol_name: str):
        uplad_link = self.get_upload_link(fol_name)
        response = requests.put(uplad_link, headers=self.get_headers(), data=open('photos.json', 'rb'))
        print(response.status_code)
        if response.status_code == 201:
            print('Загрузка прошла успешно')
