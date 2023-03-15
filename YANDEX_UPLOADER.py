import requests
import time
from progress.bar import IncrementalBar


class YaUploader:
    host = 'https://cloud-api.yandex.net/'

    def __init__(self, token: str):
        self.token = token
        self.fol_name = ''

    def get_headers(self):
        return {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.token}'}

    def set_folder_name(self, fol_name: str):
        self.fol_name = fol_name
        if '/' in self.fol_name:
            self.fol_name = self.fol_name.replace('/', '')
        if self.check_folder() != 404:
            print(f'Имя по умолчанию "{self.fol_name}" занято, придумайте имя папки самостоятельно.\n')
            self.fol_name = input('Введите название папки:\n')
            while self.check_folder() != 404:
                self.fol_name = input('Введите новое название папки:\n')
            self.create_folder()
        else:
            question = input(f'Имя по умолчанию "{self.fol_name}" свободно, использовать его? ДА/НЕТ\n')
            while True:
                if question.lower() == 'да' or question.lower() == 'нет':
                    break
                else:
                    question = input('ДА или НЕТ\n')
            if question.lower() == 'да':
                self.create_folder()
            elif question.lower() == 'нет':
                self.fol_name = input('Введите название папки:\n')
                while self.check_folder() != 404:
                    self.fol_name = input('Введите новое название папки:\n')
                self.create_folder()

    def create_folder(self):
        url = self.host + 'v1/disk/resources'
        params = {'path': f'/{self.fol_name}'}
        requests.put(url, headers=self.get_headers(), params=params)

    def check_folder(self):
        url = self.host + 'v1/disk/resources/'
        params = {'path': f'{self.fol_name}'}
        response = requests.get(url, headers=self.get_headers(), params=params)
        if response.status_code != 404:
            print(f'Папка "{self.fol_name}" уже существует.')
        return response.status_code

    def upload_photo(self, file_name, file_url):
        url_upload = self.host + 'v1/disk/resources/upload'
        count = 0
        bar = IncrementalBar('Копирование фотографий: ', max=len(file_name))
        while count < len(file_name):
            params = {'path': f'/{self.fol_name}/{file_name[count]["file_name"]}',
                      'url': f'{file_url[count]["photo_url"]}'}
            response = requests.post(url_upload, headers=self.get_headers(), params=params)
            print(response.status_code)
            count += 1
            bar.next()
            time.sleep(.75)
        bar.finish()
        self.upload(self.fol_name)

    def get_upload_link(self, fol_name):
        url = self.host + 'v1/disk/resources/upload/'
        params = {'path': f'/{fol_name}/photos.json', 'overwrite': 'true'}
        response = requests.get(url, headers=self.get_headers(), params=params)
        print(f'Получение ссылки для загрузки файла - {response.status_code}')
        return response.json()['href']

    def upload(self, fol_name: str):
        uplad_link = self.get_upload_link(fol_name)
        response = requests.put(uplad_link, headers=self.get_headers(), data=open('photos.json', 'rb'))
        if response.status_code == 201:
            print('Загрузка прошла успешно')
