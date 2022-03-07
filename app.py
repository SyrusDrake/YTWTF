import json
from datetime import datetime
from yt_dlp import YoutubeDL
import npyscreen


class Archivist():

    def __init__(self, url, cookies, filename, options) -> None:
        self.url = url
        self.cookies = cookies
        self.filename = filename
        self.options = options

    def download_list(self):
        del self.options['playlistend']
        with YoutubeDL(self.options) as ydl:
            info_dict = ydl.extract_info(self.url, download=True)

        video_list = []

        for entries in info_dict['entries']:
            try:
                title = (entries['title'])
                channel = (entries['uploader'])
                date = (entries['upload_date'])
                url = f"https://www.youtube.com/watch?v={(entries['id'])}"
                video_dict = {'title': title,
                              'channel': channel, 'date': date, 'url': url}
                video_list.append(video_dict)

            except Exception:
                video_dict = {'title': 'n/a', 'channel': 'n/a',
                              'date': 'n/a', 'url': 'n/a'}
                video_list.append(video_dict)

        with open(f'{self.filename}.json', 'w') as output:
            json.dump(video_list, output, indent=4)

    def show_title(self):
        with YoutubeDL(self.options) as ydl:
            try:
                info_dict = ydl.extract_info(self.url, download=False)
                return(info_dict['title'])
            except Exception:
                return('Playlist could not be found/accessed')


class AppWindow(npyscreen.NPSAppManaged):

    def onStart(self):
        npyscreen.setTheme(npyscreen.Themes.DefaultTheme)
        self.addForm('MAIN', SelectionForm)
        self.addForm('DOWNLOAD', DownloadForm)
        self.addForm('COMPARE', CompareForm)


class SelectionForm(npyscreen.ActionForm):
    def create(self):
        self.name = 'Select'

        self.selection = self.add(npyscreen.SelectOne, values=[
                                  'Download', 'Compare'])

    def on_ok(self):
        if self.selection.value[0] == 0:
            self.parentApp.switchForm('DOWNLOAD')
        if self.selection.value[0] == 1:
            self.parentApp.switchForm('COMPARE')

    def on_cancel(self):
        self.parentApp.switchForm(None)


class DownloadForm(npyscreen.Form):

    def create(self):
        self.name = 'Download'
        self.status = self.add(npyscreen.TitleFixedText,
                               name="Status:", value='idle')
        self.url_entry = self.add(npyscreen.TitleText,
                                  name="Playlist ID:", value='LL')
        self.cookie_src = self.add(npyscreen.TitleSelectOne, value=[
                                   0, ], name='Select Cookie Source', max_height=4, values=['cookies.txt', 'From Firefox', 'From Chrome'])
        self.b_initiate = self.add(npyscreen.ButtonPress, name='Initiate',
                                   when_pressed_function=lambda: self.initiate())
        self.pl_title = self.add(npyscreen.TitleFixedText,
                                 name="Playlist:", value='none')

    def initiate(self):
        current = datetime.now().strftime('%Y-%m-%d_(%S)')
        url = f'https://www.youtube.com/playlist?list={self.url_entry.value}'
        filename = f'{current}_dump'
        cookie = 'cookies.txt'

        if self.cookie_src.value[0] == 0:
            ydl_opts = {'cookiefile': cookie, 'simulate': True, 'ignoreerrors': True,
                        'playliststart': 1, 'playlistend': 1, 'quiet': True, 'no_warnings': True}
        elif self.cookie_src.value[0] == 1:
            ydl_opts = {'cookiesfrombrowser': ('firefox',), 'simulate': True, 'ignoreerrors': True,
                        'playliststart': 1, 'playlistend': 1, 'quiet': True, 'no_warnings': True}
        else:
            ydl_opts = {'cookiesfrombrowser': ('chrome',), 'simulate': True, 'ignoreerrors': True,
                        'playliststart': 1, 'playlistend': 1, 'quiet': True, 'no_warnings': True}

        self.app = Archivist(url, cookie, filename, ydl_opts)
        self.status.value = 'Checking Playlist, please wait.'
        self.status.display()
        response = self.app.show_title()
        self.pl_title.value = response
        self.pl_title.display()
        self.status.value = 'idle'
        self.status.display()
        if response != 'Playlist could not be found/accessed':
            self.b_download = self.add(
                npyscreen.ButtonPress, name='Archive', rely=12, when_pressed_function=lambda: self.download())
            self.b_download.display()
        self.DISPLAY()

    def download(self):
        self.status.value = 'Downloading. This may take several minutes.'
        self.status.display()
        self.app.download_list()
        self.status.value = 'Done!'
        self.DISPLAY()

    def afterEditing(self):
        self.parentApp.setNextForm(None)


class CompareForm(npyscreen.Form):
    def create(self):
        self.name = 'Compare'
        self.status = self.add(npyscreen.TitleFixedText,
                               name="Status:", value='idle')
        self.newer = self.add(npyscreen.TitleFilenameCombo, name="Newer File:")
        self.older = self.add(npyscreen.TitleFilenameCombo, name="Older File:")
        self.button = self.add(npyscreen.ButtonPress, name='Compare',
                               when_pressed_function=lambda: self.button_press(), )

    def button_press(self):
        self.status.value = 'comparing'
        self.status.display()
        missing_videos = self.find_missing(self.newer.value, self.older.value)
        self.missing_list = self.add(
            npyscreen.TitlePager, name='Missing videos:', values=missing_videos, max_height=8, rely=10)
        self.status.value = 'idle'
        self.DISPLAY()

    def find_missing(self, newer, older):
        missing_list = []
        with open(newer) as input_file:
            json_newer = json.load(input_file)
        with open(older) as input_file:
            json_older = json.load(input_file)

        list_newer = {}
        for video in json_newer:
            list_newer[video['url']] = video['title']

        list_older = {}
        for video in json_older:
            list_older[video['url']] = video['title']

        offset = len(list_newer) - len(list_older)

        for i in list_older.keys():
            if i in list(list_newer.keys())[offset:]:
                pass
            elif i == 'n/a':
                pass
            else:
                missing_list.append(list_older[i])

        missing_list.append('')
        return missing_list

    def afterEditing(self):
        self.parentApp.setNextForm(None)


if __name__ == '__main__':

    window = AppWindow()
    window.run()
