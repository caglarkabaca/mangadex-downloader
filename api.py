import requests
import json
import os

import time
from rich.progress import Progress

BASE_URL = 'https://api.mangadex.org'


class Manga:

    def __init__(self, _id, _name):
        self.id = _id
        self.name = _name


class Chapter:

    def __init__(self, _volume, _id):
        self.title = None
        self.lang = None
        self.pages = None
        self.chapter = None
        self.volume = _volume
        self.id = _id

    def get_chapter_inf(self):
        r = requests.get(f'{BASE_URL}/chapter/{self.id}')
        data = json.loads(r.content)['data']['attributes']
        self.volume = data['volume']
        self.title = data['title']
        self.chapter = data['chapter']
        self.lang = data['translatedLanguage']
        self.pages = data['pages']

    def cool_text(self) -> str:
        return f'{self.chapter} / {self.pages} pages -> {self.lang}'


# gets a list of manga with a string
def manga_list_get(string: str) -> list:
    string = string.replace(' ', '%20')
    r = requests.get(f'{BASE_URL}/manga?title={string}')
    data = json.loads(r.content)
    list_manga = []
    for sub_data in data['data']:
        _id = sub_data['id']
        titles = sub_data['attributes']['title']
        _name = titles[list(titles.keys())[0]]
        manga = Manga(_id, _name)
        list_manga.append(manga)
    return list_manga


# gets a list of chapters with a given manga id
def chapter_list_get(manga_id: str) -> list:
    list_chapters = []
    r = requests.get(f'{BASE_URL}/manga/{manga_id}/aggregate')
    data = json.loads(r.content)
    for volume in data['volumes'].values():
        for chapter in volume['chapters'].values():
            x = Chapter(str(volume), chapter['id'])
            list_chapters.append(x)
            for other in chapter['others']:
                y = Chapter(str(volume), other)
                list_chapters.append(y)
    return list_chapters


# download chapters
def download_chapters(chapters: list, path: str):
    with Progress() as progress:
        main_task = progress.add_task('[red]Getting all Chapters of manga ...', total=len(chapters))
        for chapter in chapters:
            temp_path = f'{path}/{chapter.chapter}'
            os.mkdir(temp_path)
            r = requests.get(f'{BASE_URL}/at-home/server/{chapter.id}')
            data = json.loads(r.content)

            base_url = data['baseUrl']
            _hash = data['chapter']['hash']
            data_saver = 'data-saver'
            images = [x for x in data['chapter']['dataSaver']]

            sub_task = progress.add_task(f'[blue]Downloading images of chapter {chapter.chapter} ...', total=len(images))
            for image in images:
                url = f'{base_url}/{data_saver}/{_hash}/{image}'
                with open(f'{temp_path}/{image}', 'wb') as f:
                    response = requests.get(url)
                    f.write(response.content)
                progress.update(sub_task, advance=1)
            progress.update(main_task, advance=1)

