import requests
import json
import os
import aiohttp
import aiofiles
import asyncio

from rich.progress import Progress
from rich.console import Console
console = Console()

BASE_URL = 'https://api.mangadex.org'


class Manga:

    def __init__(self, _id, _name):
        self.id = _id
        self.name = _name


class Chapter:

    def __init__(self):
        self.title = None
        self.lang = None
        self.pages = None
        self.chapter = None
        self.volume = None
        self.id = None

    async def get_chapter_inf(self, data, progress, main_task):
        self.id = data['id']
        data = data['attributes']
        self.volume = data['volume']
        self.title = data['title']
        self.chapter = data['chapter']
        self.lang = data['translatedLanguage']
        self.pages = data['pages']
        progress.update(main_task, advance=1)

    def cool_text(self) -> str:
        return f'{self.chapter} / {self.pages} pages -> {self.lang}'


class ChapterImage:

    def __init__(self, base_url, images, temp_path, i):
        self.base_url = base_url
        self.images = images
        self.temp_path = temp_path
        self.i = i


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
async def chapter_list_get(manga_id: str) -> list:
    list_chapters = []
    r = requests.get(f'{BASE_URL}/chapter?manga={manga_id}')
    data = json.loads(r.content)
    total = data['total']
    times = total // 100
    with Progress() as progress:
        main_task = progress.add_task(f'[red]Getting chapter list of given manga ...', total=total)
        for i in range(1, times + 2):
            offset = (i-1) * 100
            url = f'{BASE_URL}/chapter?manga={manga_id}&offset={offset}&limit=100'
            with requests.get(url) as resp:
                data = json.loads(resp.content)
                for sub_data in data['data']:
                    chapter = Chapter()
                    await chapter.get_chapter_inf(sub_data, progress, main_task)
                    list_chapters.append(chapter)
    return list_chapters


# download chapter
async def download_image(chapter_image, session, progress, tasks, main_task):

    for image in chapter_image.images:
        url = f'{chapter_image.base_url}/{image}'
        async with aiofiles.open(f'{chapter_image.temp_path}/{image}', 'wb') as f:
            async with session.get(url) as resp:
                await f.write(await resp.read())
                progress.update(tasks[chapter_image.i], advance=1/len(chapter_image.images))
                progress.update(main_task, advance=1)


# download chapters
async def download_chapters(chapters: list, path: str, name: str):
    os.mkdir(f'{path}/{name.replace(" ", "_")}')
    with Progress() as progress:
        async with aiohttp.ClientSession() as session:
            total = 0
            tasks = []
            download_que = []
            for c in chapters:
                tasks.append(progress.add_task(f'[blue]Downloading images of chapter {c.chapter} ...', total=1))
                total += c.pages
            main_task = progress.add_task('[red]Getting all Chapters of manga ...', total=total)
            for i, c in enumerate(chapters):
                temp_path = f'{path}/{name.replace(" ", "_")}/{c.chapter}{c.lang}'
                os.mkdir(temp_path)
                async with session.get(f'{BASE_URL}/at-home/server/{c.id}') as resp:
                    data = await resp.json()

                base_url = data['baseUrl']
                _hash = data['chapter']['hash']
                data_saver = 'data-saver'
                images = [x for x in data['chapter']['dataSaver']]

                download_que.append(ChapterImage(f'{base_url}/{data_saver}/{_hash}', images, temp_path, i))

            image_tasks = [download_image(chapter_image,
                                          session,
                                          progress,
                                          tasks,
                                          main_task) for chapter_image in download_que]

            await asyncio.gather(*image_tasks)
