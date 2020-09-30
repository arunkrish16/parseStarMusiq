class scrapper():

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
