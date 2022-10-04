from django.shortcuts import render
from .movie import *
from .scrapeTools import *

# Create your views here.
def index(request):
    return render(request, 'index.html')

# def progress(request):
#     query = request.GET['query']
#     movie_type = request.GET['movie-type']
#     download_img = request.GET['download-img']
#     form_data = [query, movie_type, download_img]
#     print(form_data)
#     return render(request, 'progress.html',{"data": query})

def progress(request):
    query = request.GET['query']
    movie_type = request.GET['movie-type']
    try:
        download_img = request.GET['download-img']
    except:
        download_img = ''

    address, movieKeyword = getAddress(movie_type, query)
    movieLinksFound, downloadLinks = recursiveScrape(find_tag('a',scrape(address)), movieKeyword.lower())    


    # option to download image
    print('='*50)
    # image_option = input("Continue to download movie image? [y/n]\nIf yes, add a search keyword or nothing to use default keyword: ").lower().split()
    image_option = download_img
    if ' '.join(image_option[1:]) == '':
        imgKeyword = movieKeyword
    else: imgKeyword = ' '.join(image_option[1:])
    if image_option == 'on':
        try:
            IMDB(imgKeyword,True,0.7)
        except:
            print("COULD NOT OBTAIN IMAGE FILE")
    imgTag = f'''style="background-image: url('./images/{imgKeyword.replace(' ', '_')}.jpg');"'''


    html_title = f'''<!DOCTYPE html>\n<html lang="en">
<head>\n<meta charset="UTF-8">\n<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{movieKeyword.capitalize()}</title>\n<link rel="stylesheet" href="../styles.css">
</head>\n<body>\n<section class="movieLinks" style="background-image: url('../images/{movieKeyword.replace(' ', '_')}.jpg');">'''
    
    if len(movieLinksFound) > len(movieKeyword)+15:
        # saveAs(movieLinksFound,movieKeyword+"(recursive)",'.txt','w')                  # saves ONCE as TXT file
        
        ends_with = "</u>\n</section>\n</body>\n</html>"
        saveAs(html_title,'movie_website/html/'+movieKeyword,'.html','w')       # writing down the html boiler plate first with 'w' to overrite text in file if pressent
        saveAs(downloadLinks+ends_with,'movie_website/html/'+movieKeyword,'.html')    # saves ONCE as HTML file
        
        indexHTML_code = f'''\n<a href="./html/{'_'.join(movieKeyword.split())}.html"><div class='box_nav' {imgTag}><h1>{movieKeyword.capitalize()}</h1></div></a>'''
        saveAs(indexHTML_code,'movie_website/index','.html')                    # main navigation to connect to DOWNLOAD LINK HTML

        directory = "file://c:/users/esmon/desktop/scrapes/movie_website/index.html"
        print("**__SUCCESS__**\nOpen html link: ", directory)
    else:   print("!!__MOVIE LINK SEARCH NOT SUCCESSFUL__!!")
