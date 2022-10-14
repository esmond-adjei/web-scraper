from django.shortcuts import render
from .movie import *
from .scrapeTools import IMDB

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
    scraped_data = recursiveScrape(find_tag('a',scrape(address)), movieKeyword.lower())    
    image_option = download_img

    # option to download image
    print('='*50)
    if ' '.join(image_option[1:]) == '':
        imgKeyword = movieKeyword
    else: imgKeyword = ' '.join(image_option[1:])
    if image_option == 'on':
        try:
            IMDB(imgKeyword,True,0.7)
        except:
            print("COULD NOT OBTAIN IMAGE FILE")
        
    print("========== data ============\n")
    for k,v in scraped_data.items():
        print('>>',k,'\n\t',v)
    
    return render(request, 'progress.html', {'scraped_data': scraped_data})

