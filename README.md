# YTWTF

## What does it do?
When a video is removed from YouTube, by deletion, making it private, or any other means, it leaves no "trace". If you have added it to a playlist, you will only see a removed video, without knowing what it was. 

This app lets you download a "snapshot" of a playlist, which it stores as json. It also lets you compare two of those json-files and lists all videos that went "missing" between snapshots. 

## Download playlist info

The app runs inside the terminal with a simple GUI. Upon launch, you are prompted to select "Download" or "Compare". Select "Download" and then "OK" at the bottom of the window. 

On the next screen, you can choose are few options:

**Playlist ID**  
This app is primarily intended and optimized for the "Liked Videos" playlist. This is also the default option. If you want, you can choose another ID and paste it here. Paste *only* the ID, i.e. the part after "list=" in the playlists' url. 

**Select Cookie Source**  
For any private playlists, which includes "Liked Videos", you'll need to provide a cookie file from a logged-in YT page. The most robust way is to provide a cookie file called "cookies.txt" in the folder the application is running in. The easiest way to get your cookie file is to use a browser extension ([Firefox](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/), [Chrome](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid?hl=en))  
The app can also attempt to extract the necessary cookies from your browser itself. I have only tested this for Firefox and only on my machine. **I do not know how well this works on other machines!**

Once you selected a playlist and a cookie source, press "Initiate". The app will check if the playlist ID you gave it actually exists. If it does, you can then start the download process by pressing "Download" (this will only show up once you have Initiated the process). 

**!!THIS PROCESS MAY TAKE A LONG TIME!!**  
Fetching the data of one video takes about 1-2 seconds. If you have hundreds of videos in your playlist, this may take several minutes. You will know that the process is finished once the GUI restores and the status text switches to "Done!". The result will be automatically saved as a json dump named after the current date (plus some "ID" based on the current second to reduce the risk of file name collisions). 

## Compare lists

If you choose "Compare" on the main screen, you will be presented with two file selection prompts. Select the newer file first, the older file second and press "Compare". Both lists will be compared and you will be presented with a list of titles of videos that, for one reason or another, went "missing" between snapshots.

## Limitations and known issues

This app started out as a private project. I then decided to make it *somewhat* useable for other people. There are still some limitations though. There are also some issues I am aware of but can't fix.

- This app was written and tested on a Linux machine. I think it should work on any OS but have not confirmed this yet. 
- The "Download" button will come after the "OK" button on the Download screen in the selection order. I don't know why that is.
- If yt_dlp, which is the library that handles communication with Youtube, comes across a missing video in a playlist, it prints out an error, which overwrites the CLI. I can not turn off this error printout. If you're downloading a playlist with a lot of missing videos, the interface will be overwritten completely. However, it will be restored once the download is finished, so just ignore the printouts.
- This is also true for an error that gets thrown if you input an invalid playlist ID.
- The file input for the snapshot comparison is not sanitized at all. You can select any file and any snapshot in any order. It's up to you to make sure you select the newer json first and the older json second.
- The comparison function assumes that any missing video is missing because it got deleted or otherwise removed. It also assumes playlists either stay the same length or grow. If you're removing videos manually between snapshots, the results will not be accurate anymore. 
- If the app comes across a missing video, it puts down the title as "n/a". If you have an actual video titles "n/a" in your playlist, it will be ignored and its removal would not be detected. 
