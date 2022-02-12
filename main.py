import api
import questionary
import asyncio
from rich.progress import track

with open('.ver') as f:
    VER = f.read()


async def main():
    await questionary.text('Thanks for choosing our Mangadex downloader...').ask_async()
    await questionary.text(f'Version [{VER}]').ask_async()
    name = await questionary.text('Name of Manga : ').ask_async()
    temp: list = api.manga_list_get(name)
    choice = await questionary.select(
        "Select the name of Manga, you wanna download",
        choices=[x.name for x in temp]).ask_async()
    for x in temp:
        if choice == x.name:
            choice = x
    temp: list = await api.chapter_list_get(choice.id)

    # for n in track(range(len(temp)), description='Getting information of all chapters...'):
    #   temp[n].get_chapter_inf()

    questionary.text('chapter / page count -> language ')
    choices = await questionary.checkbox(
        "Select the chapters of Manga, you wanna download",
        choices=[x.cool_text() for x in temp]).ask_async()
    for chapter in temp:
        for index, choice in enumerate(choices):
            if choice == chapter.cool_text():
                choices[index] = chapter

    path = await questionary.path("Please select the path where do you want these Chapters downloaded at?").ask_async()
    api.download_chapters(choices, path)

    await questionary.text('Download successful, at least we hope ').ask_async()


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
