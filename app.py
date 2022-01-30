import json
from datetime import datetime
from yt_dlp import YoutubeDL
import npyscreen

# def my_hook(d):
#     print('hook')
#     if d['status'] == 'downloading':
#         print(f'downloading')
#     if d['status'] == 'finished':
#         print('Done downloading, now converting ...')
#         return d


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
                video_dict = {'title': 'n/a', 'channel': 'n/a', 'date': 'n/a'}
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

    def find_missing(self, file1, file2):
        missing_list = []
        with open(file1) as input_file:
            json_1 = json.load(input_file)
        with open(file2) as input_file:
            json_2 = json.load(input_file)

        list_1 = []
        for video in json_1:
            list_1.append(video['title'])

        list_2 = []
        for video in json_2:
            list_2.append(video['title'])
        offset = len(list_1) - len(list_2)

        for i in list_2:
            if i in list_1[offset:]:
                pass
            elif i == 'n/a':
                pass
            else:
                missing_list.append(i)

        missing_list.append('')
        return missing_list

    def afterEditing(self):
        self.parentApp.setNextForm(None)


if __name__ == '__main__':

    window = AppWindow()
    window.run()
