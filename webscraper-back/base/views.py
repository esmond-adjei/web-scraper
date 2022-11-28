from django.shortcuts import render
from .scrapealgo import *
from .scrapeTools import IMDB

# Create your views here.

PAYLOAD = {}


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

    if query.strip().replace("+", "") == '':
        scraped_data = {}
    else:
        address, movieKeyword = getAddress(movie_type, query)
        scraped_data = recursiveScrape(
            find_tag('a', scrape(address)), movieKeyword.lower())

    # option to download image
    print('='*50)
    if download_img == 'yes':
        try:
            imglnk = IMDB(query, True, 0.7)
            # print(imglnk)
        except:
            print("COULD NOT OBTAIN IMAGE FILE")
            imglnk = '#'
    else:
        imglnk = '#'
    # print("========== data ============\n")
    # for k, v in scraped_data.items():
    #     print('>>', k, '\n\t', v)
    scraped_data = {k: v for k, v in scraped_data.items() if v}

    PAYLOAD = {'scraped_data': scraped_data, 'query': query, 'imglnk': imglnk}
    return render(request, 'progress.html', {'payload': PAYLOAD})
