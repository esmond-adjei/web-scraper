import bs4
import requests
import io
from PIL import Image

"""
    1. obtain address
    2. get webpage
    3. compare search key(movie) with link texts
    4. get second webpage from link in related texts from step 3
    5. compare resolution(1080p/720p/480p) with linked texts
    6. get all related links that satisfy step 5 and save in a file.
"""

"""
   a. get to the page -- requests.get(address)  ------->> scrape function
      create a soup  --- bs4.BeautifulSoup(address.text, 'html.parser') 
   b. get all anchor-link-tags or any other tag(eg: 'img')  --- soup.find_all('a')  -----> find_tag
   c. sort links by type |movie |html | arbitrary-keyword   ----->  find_by_keyword 
   d. do what you want with the sorted links::: save as text, scrape, download, print
"""

# INPUT OPERATIONS


def getAddress(movie_type, query):
    '''
        1. Take user input (command for movie type and movie title) data from terminal
        2. Gets appropriate address based on command and creates an search query address with the movie title
        3. Returns MOVIE ADDRESS and MOVIE SEARCH KEYWORD.
    '''
    # making address for LIGHTDLMOVIES
    addressDictionary = {
        "series": "https://lightdlss.blogspot.com/search?q=",
        "movie": "https://lightdlmovies.blogspot.com/search?q=",
        "anime": "https://lightdlsite.blogspot.com/search?q=",
        "h": "https://hdmoviesringo.in/?s=",
        "H": "https://movieshippo.in/?s=",
    }

    websiteType = movie_type
    movie_query = query
    movie_keyword = ''
    if movie_keyword == '':
        movie_keyword = movie_query

    # website address + search
    full_address = addressDictionary[websiteType] + \
        movie_query.replace(' ', '+')
    print("\nGetting Link...")

    return full_address, movie_keyword


def scrape(addr):
    """ scrapes and address and returns the response object """
    try:
        print(f"\nSCRAPING.. @ {addr}\n")
        response = requests.get(addr)
        return response
    except Exception:
        print('UNABLE TO EXTABLISH A CONNECTION WITH %s' % addr)
        # exit()
        return

# PROCESSING
# FIND KEYS


def find_tag(tag, response):
    """ create a soup object and returns an object of a particular tag """
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    return list(soup.find_all(tag))


def find_by_keyword(keyword, list_of_related_links):
    """
       searches through list of links for the link that has the keyword and returns the link
    """
    keyword_list = []
    if not list_of_related_links:
        return print("EMPTY or TYPE NOT LIST WAS PASSED. Type =", type(list_of_related_links))
    else:
        for each_link_tag in list_of_related_links:
            try:
                if keyword in each_link_tag.get("href").lower():
                    keyword_list.append(each_link_tag)
            except:
                pass  # f"{keyword}\nNoneType encountered")
    return keyword_list


def find_type(link, extension_type):
    """ checks if a link is of particular type by 
        checking if extension type elements is in link
        eg: link: 'https://google.com/search?q=home.html' extension_type: html = ('.html', '.htm') or video = ('.mp4', '.mkv')
        returns true or false
    """
    for e_type in extension_type:
        if e_type == link[-len(e_type):]:
            return True
    return False


def find_text(keyword, list_of_tags):
    filtered_list = []
    for tag in list_of_tags:
        try:
            if compareLists(keyword.split(), tag.text.lower().split()):
                filtered_list.append(tag)
        except:
            continue
    return filtered_list


def compareLists(lista, listb):
    ''' compares elements of two list and returns TRUE if there is an intercession(common) element between them'''
    counter = 0
    for e in lista:
        for f in listb:
            if e in f:
                counter += 1
            if counter == 2:
                return True
    if counter == 1:
        return True
    else:
        return False

# GET IMAGE


def IMDB(movieKeyword, compress=False, compression_factor=1):
    """ download image from IMDB.COM and compresses the file"""

    # create IMDB equivalent address
    imgAddress = 'https://imdb.com/find?q='+movieKeyword.replace(' ', '+')
    imgAddress = 'https://imdb.com'+find_text(movieKeyword, find_tag('a', scrape(
        imgAddress)))[0].get("href")     # scrape and get first link with KEYWORD in TEXT
    # scrape and select first link with 'mediaviewer' in LINK
    imageLink = 'https://imdb.com' + \
        find_by_keyword('mediaviewer', find_tag(
            'a', scrape(imgAddress)))[0].get("href")
    # choose image from here
    image = find_tag('img', scrape(imageLink))[0].get("src")
    # scrape the image bytes
    # image = scrape(image).content
    # Next three lines compress the image file
    # image = Image.open(io.BytesIO(image))

    return image

    if compress:
        h, w = image.size
        image = image.resize(
            (int(h*compression_factor), int(w*compression_factor)), Image.ANTIALIAS)

    savePath = "C:/Users/HP/Desktop/scrapes/movie_website/images/" + \
        movieKeyword.replace(' ', '_')+'.jpg'
    image.save(savePath)
    print(f"IMAGE OF {movieKeyword.upper()} SAVED SUCCESSFULLY")


# OUTPUT
# SAVE TO LOCAL
def saveAs(data, filename, extension='.txt', writeType='a', path="C:/Users/esmon/Desktop/scrapes/"):
    with open(path+'_'.join(filename.capitalize().split())+extension, writeType) as movieFile:
        movieFile.write(data)
