from django.shortcuts import render
from .scrapealgo import *
from .scrapeTools import IMDB

import json
# Create your views here.


def index(request):
    return render(request, 'index.html')


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

    scraped_data = {k: v for k, v in scraped_data.items() if v}

    PAYLOAD = {'scraped_data': scraped_data, 'query': query, 'imglnk': imglnk}
    with open('tmp.json', 'w') as wf:
        print("\n-->> Saving to JSON\n")
        json.dump(PAYLOAD, wf, indent=2)

    return render(request, 'progress.html', {'payload': PAYLOAD})


def save(request):

    with open('tmp.json') as rf:
        print("\n-->> Reading JSON\n")
        PAYLOAD = json.load(rf)
    return render(request, 'save.html')
