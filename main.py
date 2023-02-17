import requests
# from pprint import pprint
from datetime import datetime
import time
import json
from progress.bar import IncrementalBar


def get_token():
  with open('token_vk.txt', 'r') as file:
    return file.readline()


class VK:
  def __init__(self, access_token, user_id, version='5.131'):
    self.token = access_token
    self.id = user_id
    self.version = version
    self.params = {'access_token': self.token, 'v': self.version}

  def user_private(self):
    url = 'https://api.vk.com/method/users.get'
    params = {'user_ids': self.id}
    response = requests.get(url, params={**self.params, **params})
    json_res = response.json()
    return (json_res['response'][0]['can_access_closed'])

  def users_photo(self, count_photos: int):
    photos = []
    photo_dict = {}
    url = 'https://api.vk.com/method/photos.get'
    params = {
      'owner_id': self.id,
      'album_id': 'profile',
      'extended': 1,
      'count': count_photos
    }
    response = requests.get(url, params={**self.params, **params})
    json_res = response.json()
    bar = IncrementalBar('Loading', max=len(json_res['response']['items']))
    print('Загрузка фото профиля:')
    for photo in range(len(json_res['response']['items'])):
      photo_dict = {
        'url_photo': json_res['response']['items'][photo]['sizes'][-1]['url'],
        'name_photo': json_res['response']['items'][photo]['likes']['count'],
        'type_size': json_res['response']['items'][photo]['sizes'][-1]['type'],
        'date_photo': json_res['response']['items'][photo]['date']
      }
      photos.append(photo_dict)
      bar.next()
      time.sleep(0)
    bar.finish()
    return photos  # получим список словарей с данными по фото

  def user_profile_photo_exist(self):
    url = 'https://api.vk.com/method/photos.get'
    params = {
      'owner_id': self.id,
      'album_id': 'profile',
      'extended': 1,
      'count': 1
    }
    response = requests.get(url, params={**self.params, **params})
    json_res = response.json()
    if json_res['response']['count'] != 0:
      return (True)
    else:
      return (False)

class YA_Disk:

  def __init__(self, _token: str):
    self.token = _token

  def create_json_file(self, json_list: []):
    jsonString = json.dumps(json_list, indent=2)
    with open('new_file.json', 'w') as f:
      f.write(jsonString)
    print('\n')
    print('json-file создан')
  
  def create_folder(self, name_folder):
    upload_url = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {'Content-type': 'application/json', 'Authorization': self.token}
    params = {'path': name_folder}
    res = requests.put(upload_url, headers=headers, params=params)
    json_res = res.json()
    if res.status_code == 409:
      print(json_res['message'])
      return (False)
    elif res.status_code == 201:
      print('Папка ' + f'{name_folder}' + ' создана')
      return (True)

  
  def copy_photo(self, photos: [], name_folder: str):
    json_list=[]
    name_photos = []
    bar = IncrementalBar('Loading', max=len(photos))
    print('Загрузка фото на Яндекс.Диск:')
    for photo in range(len(photos)):
      name_photo = photos[photo]['name_photo']
      if name_photo in name_photos:
        date_photo = datetime.fromtimestamp(photos[photo]['date_photo'])
        name_photo = f'{name_photo}' + '_' + f'{date_photo.date()}'
      upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
      headers = {
        'Content-type': 'application/json',
        'Authorization': self.token
      }
      params = {
        'path': '/' + f'{name_folder}' + '/' + f'{name_photo}',
        'url': photos[photo]['url_photo']
      }
      requests.post(upload_url, headers=headers, params=params)
      json_list.append({'file_name': name_photo, 'size': photos[photo]['type_size']})
      name_photos.append(name_photo)  # список для проверки на совпадение имен
      bar.next()
      time.sleep(0)
    self.create_json_file(json_list) #создание json-файла
    bar.finish()



if __name__ == '__main__':
  user_id = input('Введите id пользователя:\n')  # '4584140' #'458997111'

  access_token = get_token()
  vk = VK(access_token, user_id)

  if vk.user_private() is True:  # если профиль открыт
    if vk.user_profile_photo_exist(
    ) == True:  #если у пользователя есть фото профиля
      count_photos = input('Введите количество фото:\n')
      if count_photos == '':
        count_photos = '5'
      access_token = input(
        'Введите токен Я.Диска:\n'
      )  # access_token = 'y0_AgAAAAATyN3PAADLWwAAAADalLv5SmLMDPA1T3imDXdMLgVfDQInee8'
      folder_name = input('Введите имя папки:\n')
      ya = YA_Disk(access_token)

      if ya.create_folder(folder_name) == True:  # создать папку
        ya.copy_photo(vk.users_photo(count_photos),
                      folder_name)  # скопировать фото

      else:
        print('Невозможно скопировать файлы в существующую папку')
    else:
      print('У данного пользователя нет фото профиля')
  else:
    print('Профиль пользователя закрыт')
