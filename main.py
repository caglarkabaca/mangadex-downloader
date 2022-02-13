import api
import questionary
import asyncio

from questionary import Style
from questionary import Choice, Separator

css = Style([
    ('qmark', 'fg:#ff0000 bold'),       # token in front of the question
    ('question', 'bold'),               # question text
    ('answer', 'fg:#f44336 bold'),      # submitted answer text behind the question
    ('pointer', 'fg:#673ab7 bold'),     # pointer used in select and checkbox prompts
    ('highlighted', 'fg:#673ab7 bold'), # pointed-at choice in select and checkbox prompts
    ('selected', 'fg:#cc5454'),         # style for a selected item of a checkbox
    ('separator', 'fg:#cc5454'),        # separator in lists
    ('instruction', '#ffce38 bold italic'),                # user instructions for select, rawselect, checkbox
    ('text', 'bold'),                       # plain text
    ('disabled', 'fg:#858585 italic')   # disabled choices for select and checkbox prompts
])


async def main():
    await questionary.text(f'Thanks for choosing our Mangadex downloader... \n      v0.3.0 ...', style=css).ask_async()
    name = await questionary.text('Name of Manga : ', style=css).ask_async()
    temp: list = api.manga_list_get(name)
    choice = await questionary.select(
        "Select the name of Manga, you wanna download",
        choices=[Choice(x.name) for x in temp], style=css).ask_async()
    name = choice
    for x in temp:
        if choice == x.name:
            choice = x
    temp: list = await api.chapter_list_get(choice.id)

    questionary.text('chapter / page count -> language ')
    choices = await questionary.checkbox(
        "Select the chapters of Manga, you wanna download",
        choices=[Choice(x.cool_text()) for x in temp], style=css).ask_async()
    for chapter in temp:
        for index, choice in enumerate(choices):
            if choice == chapter.cool_text():
                choices[index] = chapter

    path = await questionary.path("Please select the path where do you want these Chapters downloaded at?",
                                  style=css).ask_async()
    await api.download_chapters(choices, path, name)

    await questionary.text('Download successful, at least we hope ', style=css).ask_async()


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
