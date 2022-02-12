import api
import questionary
from rich.progress import track

with open('.ver') as f:
    VER = f.read()


def main():
    questionary.text('Thanks for choosing our Mangadex downloader...').ask()
    questionary.text(f'Version [{VER}]').ask()
    name = questionary.text('Name of Manga : ').ask()
    temp: list = api.manga_list_get(name)
    choice = questionary.select(
        "Select the name of Manga, you wanna download",
        choices=[x.name for x in temp]).ask()
    for x in temp:
        if choice == x.name:
            choice = x
    temp: list = api.chapter_list_get(choice.id)
    for n in track(range(len(temp)), description='Getting information of all chapters...'):
        temp[n].get_chapter_inf()
    questionary.text('chapter / page count -> language ')
    choices = questionary.checkbox(
        "Select the chapters of Manga, you wanna download",
        choices=[x.cool_text() for x in temp]).ask()
    for chapter in temp:
        for index, choice in enumerate(choices):
            if choice == chapter.cool_text():
                choices[index] = chapter

    path = questionary.path("Please select the path where do you want these Chapters downloaded at?").ask()
    api.download_chapters(choices, path)

    questionary.text('Download successful, at least we hope ').ask()


if __name__ == '__main__':
    main()
