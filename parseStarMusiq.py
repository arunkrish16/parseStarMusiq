#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is a not a general purpose script.
This script helps in scrapping and downloading the Music files from starmusiq.fun website.
"""

import requests
from bs4 import BeautifulSoup
import zipfile
import io
import sys

baseURL = "https://www.starmusiq.fun"
navURLs = { "top25":"/player/top-25-hits-by-year-month-week-starmusiq.html",
            "latest":"/latest/latest-2018-movie-songs-starmusiq.html",
            "composer":"/composers/list-of-music-composers-starmusiq.html",
            "movies": "/search/search-for-blocked-movies-starmusiq.html"}
navByPage = True
downloadIndividualSong = True


def browsePage(baseURL, navURL=""):
    try:
        page = requests.get(baseURL + navURL)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup
    except requests.exceptions.RequestException as e:
        print("URL not reachable")
        print(e)
        callQuit()


def scrapTop25List(soup):
    for div in soup.find_all("div", {"id": "hits_list"}):
        for a in div.find_all("a", {"class": "text-warning"}):
            songName = a.parent.parent.find("a").text.split(" - ")[0] + " - " + a.text
            navURL = a["href"]
            yield songName, baseURL, navURL


def scrapComposerList(soup):
    for a in soup.find_all("a"):
        if a.text == "View Movies":
            composerName = a["title"].split(" - ")[0][5:]
            navURL = a["href"]
            yield composerName, baseURL, navURL
    if navByPage :
        for a in soup.find_all("a", {"aria-label" : "Previous"}):
            navURL = a["href"]
            yield "Previous...", baseURL, navURL
        for a in soup.find_all("a", {"aria-label" : "Next"}):
            navURL = a["href"]
            yield "Next...", baseURL, navURL
    else:
        for a in soup.find_all("a", {"aria-label" : "Next"}):
            navURL = a["href"]
            soup = browsePage(baseURL, navURL)
            yield from scrapComposerList(soup)


def scrapLatestList(soup):
    # since latest list and movie list are same, use the same function.
    yield from scrapMovieList(soup)


def scrapMovieList(soup):
    for a in soup.find_all("a"):
        if (a.text == "Download Album") and not ("single" in a["href"]):
            movieName = a["title"].split(" - ")[0]
            navURL = a["href"]
            yield movieName, baseURL, navURL
    if navByPage :
        for a in soup.find_all("a", {"aria-label" : "Previous"}):
            navURL = a["href"]
            yield "Previous...", baseURL, navURL
        for a in soup.find_all("a", {"aria-label" : "Next"}):
            navURL = a["href"]
            yield "Next...", baseURL, navURL
    else:
        for a in soup.find_all("a", {"aria-label": "Next"}):
            navURL = a["href"]
            soup = browsePage(baseURL, navURL)
            yield from scrapMovieList(soup)


def scrapSongList(soup):
    for a in soup.find_all("a"):
        if a.text.upper() == "DOWNLOAD 320KBPS":
            songName = a.parent.previous_sibling.find("a").text.split(" - ")[0]
            baseURL = a["href"].split("?")[0]
            navURL = "?" + a["href"].split("?")[1]
            yield songName, baseURL, navURL


def scrapAllSongZipfile(soup):
    found = False
    # Try with CSS Selector
    for div in soup.select("html body div.container div.row div.col-xs-12.col-sm-12.col-md-8 div.panel.panel-default div.panel-body div.row div.panel.panel-danger div.panel-body div.row div.col-md-8"):
        for a in div.find_all("a"):
            if "320KBPS" in str(a.text).upper():
                found = True
                songZipFileName = a.text
                baseURL = a["href"].split("?")[0]
                navURL = "?" + a["href"].split("?")[1]
                yield songZipFileName, baseURL, navURL
    # Try with keywords in <a> tags
    if not found:
        for a in soup.find_all("a"):
            if ("320KBPS ZIP FILE" or "320KBPS ZIP" or "320KBPS LINK") in str(a.text).upper():
                found = True
                songZipFileName = a.text
                baseURL = a["href"].split("?")[0]
                navURL = "?" + a["href"].split("?")[1]
                yield songZipFileName, baseURL, navURL

    if not found:
        print("Cannot find 320KBPS download file. For manual download use the below url..")
        yield found


def scrapDownloadLink(soup):
    found = False
    for a in soup.find_all("a"):
        if "Download Now" in a.text:
            found = True
            navURL = a["href"]
            yield navURL
    if not found:
        print("Cannot find Download link. For manual download use the below url..")
        yield found


def downloadAndExtract(url, songName = ''):

    try:
        print("Starting to download...")
        r = requests.get(url)
        print("Download Completed !!!")

        if not downloadIndividualSong:
            try:
                print("Starting to extract...")
                z = zipfile.ZipFile(io.BytesIO(r.content))
                z.extractall("../Downloads/")
                print("Extraction Completed !!!")
            except:
                print("Couldnot Extract File. For manual download use the following url..")
                print(url)
        else:
            try:
                print("Saving File...")
                with open("../Downloads/" + songName, 'w') as s:
                    s.write(io.BytesIO(r.content))
                print("Completed !!!")
            except:
                print("Couldnot save File. For manual download use the following url..")
                print(url)


    except:
        print("Cannot Download File. For manual download use the following url..")
        print(url)


def decodeSelection(keyInput, menuListLength):
    selectList = []
    for i in keyInput.split(","):
        if "q" in i:
            callQuit()
        elif ":" in i:
            l, h = map(int, i.split(":"))
            selectList += range(l, h+1)
        else:
            selectList.append(int(i))
    for i in selectList:
        if i > menuListLength:
            print("Enter Valid Selection")
            yield from decodeSelection(keyInput, menuListLength)
    for i in selectList:
        yield i - 1


def getSelectionList(baseURL, navURL, scrapType):

    soup = browsePage(baseURL, navURL)

    menuListLength = 0
    for index, menuItem in enumerate(scrapTypeList[scrapType](soup)):
        print(index + 1, menuItem[0], menuItem[1], menuItem[2])
        menuListLength += 1

    keyInput = input("Enter selection(s) (Comma separated for multiples or Colon for range) or q to Quit\n: ")

    for index, menuItem in enumerate(scrapTypeList[scrapType](soup)):
        if index in decodeSelection(keyInput, menuListLength):
            if menuItem[0] == "Next...":
                print("Getting next page..")
                navURL = menuItem[2]
                yield from getSelectionList(baseURL, navURL, scrapType)
            elif menuItem[0] == "Previous...":
                print("Getting previous page..")
                navURL = menuItem[2]
                yield from getSelectionList(baseURL, navURL, scrapType)
            else:
                menuName = menuItem[0]
                baseURL = menuItem[1]
                navURL = menuItem[2]
                yield menuName, baseURL, navURL


def callQuit():
    try:
        sys.exit(0)
    except SystemExit as e:
        pass


def main():

    def getTop25(baseURL, navURL):
        # global downloadIndividualSong = True
        for movie in getSelectionList(baseURL, navURL, "top25"):
            soup = browsePage(movie[1], movie[2])
            for song in scrapSongList(soup):
                if movie[0].split(" - ")[0].upper() == song[0].upper():
                    print("Getting download url for song", song[0])
                    soup = browsePage(song[1], song[2])
                    for url in scrapDownloadLink(soup):
                        if not url:
                            print(url)
                        else:
                            print("Downloadable", song[1] + url)
                            downloadAndExtract(song[1] + url, song[0])

    def getLatest(baseURL, navURL):
        for movie in getSelectionList(baseURL, navURL, "latest"):
            print("Getting song list of", movie[0])
            if downloadIndividualSong:
                getSongList(movie[1], movie[2])
            else:
                getSongBulk(movie[1], movie[2])

    def getComposer(baseURL, navURL):
        for composer in getSelectionList(baseURL, navURL, "composer"):
            print("Getting movie list of", composer[0])
            getMovie(composer[1], composer[2])

    def getMovie(baseURL, navURL):
        for movie in getSelectionList(baseURL, navURL, "movie"):
            print("Getting song list of", movie[0])
            if downloadIndividualSong:
                getSongList(movie[1], movie[2])
            else:
                getSongBulk(movie[1], movie[2])

    def getSongList(baseURL, navURL):
        for song in getSelectionList(baseURL, navURL, "song"):
            print("Extracting download url for song", song[0])
            soup = browsePage(song[1], song[2])
            for url in scrapDownloadLink(soup):
                if not url:
                    print(url)
                else:
                    print("Downloadable", song[1] + url)
                    # downloadAndExtract(url)

    def getSongBulk(baseURL, navURL):
        soup = browsePage(baseURL, navURL)
        for song in scrapAllSongZipfile(soup):
            if not song:
                print(baseURL + navURL)
            else:
                print("Extracting download url")
                soup = browsePage(song[1], song[2])
                for url in scrapDownloadLink(soup):
                    if not url:
                        print(url)
                    else:
                        print("Downloadable", song[1] + url)
                        # downloadAndExtract(url)

    keyInput = input("Enter Selection:\n\t1 for Top 25\n\t2 for Latest\n\t3 for Composer List\n\t4 for Movie List\n: ")


    if keyInput == "1":
        print("Getting list of Top 25 songs...")
        navURL = navURLs["top25"]
        getTop25(baseURL, navURL)

    elif keyInput == "2":
        print("Getting list of latest movies...")
        navURL = navURLs["latest"]
        getLatest(baseURL, navURL)

    elif keyInput == "3":
        print("Getting list of composers..")
        navURL = navURLs["composer"]
        getComposer(baseURL, navURL)

    else:
        print("Getting list of movies...")
        navURL = navURLs["movies"]
        getMovie(baseURL, navURL)


if __name__ == "__main__":
    scrapTypeList = {   "top25":scrapTop25List,
                        "latest":scrapLatestList,
                        "composer":scrapComposerList,
                        "movie":scrapMovieList,
                        "song":scrapSongList,
                        "songBulk": scrapAllSongZipfile}
    main()

