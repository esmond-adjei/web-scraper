from .scrapeTools import *


def recursiveScrape(list_of_links, keyword):
    """
    For each LINK TAG in list of links,
        1. if KEYWORD is in LINK TEXT __(fn: compareList)__ then 
            a. check if LINK TYPE (__fn: __) is MOVIE then 
                - print MOVIE NAME on console
                - add LINK to "list" of FOUND MOVIE LINKS
                - save LINK as TEXT FILE __(fn: saveAs)__ with KEYWORD as filename 
            b. else if LINK type is HTML then
                - scrape the HTML link __(fn: scrape)__
                - carry out 1a on RESPONSE 
        return FOUND MOVIE LINKS
    """
    movieLinksFound, downloadLinks,  = '',''
    count, count2, season = 1,1,1
    
    if not list_of_links:   print("NoneType NoneType NoneType")
    else:
        for link_tag in list_of_links:
            if compareLists(keyword.split(), link_tag.text.lower().split()):     # compares keyword and text on the site
                link = link_tag.get("href")
                if link[-3:] in ("mkv", "mp4"):
                    movieLink = link.strip()
                    # print(">> Movie Link: ", movieTitle)
                    
                    if f's0{season}' in link_tag.get("href").lower():           # executed for seaonal movies. It counts the seasons
                        movieLinksFound += "\n\t____SEASON {}____\n".format(season)
                        downloadLinks += "</ul>\n\n<ul class='box_link'><h2>{} SEASON {}</h2>\n".format(movieTitle,season)
                        season += 1
                        count = 1
                    
                    movieLinksFound += "{}) {}\n".format(count, movieLink)
                    downloadLinks += "\t<li><a href=\"{}\">{}. {}</a></li>\n".format(movieLink,count,movieTitle)    # generate list of links
                    count += 1
                elif link[-4:] in ("html",".htm"):                  # usually implemented once:: gateway to page with download links
                    htmlLink = link
                    #print("HTML Link: ",htmlLink)
                    movieTitle = link_tag.text.strip().replace('.',' ')
                    print("MOVIE TITLE: ",movieTitle)
                    movieLinksFound += "\n\t({})____{}____\n".format(count2,movieTitle)
                    downloadLinks += "</ul>\n\n<ul class='box_link'><h2>{}. {}</h2>\n".format(count2,movieTitle)

                    count2 += 1
                    count = 1

                    foundLinks = find_tag('a', scrape(htmlLink))    # rescrape to get to the LINKS
                    if foundLinks:                                  # to ensure that we do not recursiveScrape an empty list
                        continue
                    recursiveScrape(foundLinks,keyword)
    return movieLinksFound, downloadLinks
        
