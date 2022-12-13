from django.shortcuts import render, redirect
from .scrapealgo import *
from .scrapeTools import IMDB

from .models import Movie
from .form import RegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

import json
# Create your views here.


def registerPage(request):
    registerForm = RegisterForm()
    if request.method == 'POST':
        registerForm = RegisterForm(request.POST)
        if registerForm.is_valid():
            registerForm.save()
            # user = registerForm.clean_data.get('username')
            # messages.success(request, 'Account was created for' + user)

            return redirect('login')

    context = {'form': registerForm}
    return render(request, 'register.html', context)


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'username OR password is incorrect')

    context = {}
    return render(request, 'login.html', context)


def index(request):
    try:
        movie_data = Movie.objects.all()
    except:
        print("User not logged in, yet")  # This is not true as of 2022/12/11

    return render(request, 'index.html', {'movie_data': movie_data})


def progress(request):

    query = request.GET['query']
    # if query exists fetch from database else scrape online
    movie_obj_db = Movie.objects.filter(query=query)
    if len(movie_obj_db):
        PAYLOAD = {}
        PAYLOAD['imglnk'] = fetch_from_db(movie_obj_db[0])['imglnk']
        PAYLOAD['scraped_data'] = fetch_from_db(movie_obj_db[0])[
            'scraped_data']
        for movie_obj_index in range(1, len(movie_obj_db)):
            PAYLOAD['scraped_data'].update(fetch_from_db(
                movie_obj_db[movie_obj_index])['scraped_data'])

    else:
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
                imglnk = IMDB(query)
            except:
                print("COULD NOT OBTAIN IMAGE FILE")
                imglnk = '#'
        else:
            imglnk = '#'

        scraped_data = {k: v for k, v in scraped_data.items() if v}

        PAYLOAD = {'scraped_data': scraped_data,
                   'query': query, 'imglnk': imglnk, 'scraped': True}
        with open('tmp.json', 'w') as wf:
            json.dump(PAYLOAD, wf, indent=2)

    return render(request, 'progress.html', {'payload': PAYLOAD})


def save(request):

    with open('tmp.json') as rf:
        PAYLOAD = json.load(rf)

    created = False
    for movie, links in PAYLOAD['scraped_data'].items():
        # 'get_or_create()' -> checks if not present then create, else get. But we use the get for nothing

        if movie not in request.user.movie_set.all():
            Movie.objects.get_or_create(
                username=request.user,
                query=PAYLOAD['query'],
                moviename=movie,
                movielink=", ".join(links),
                imagelink=PAYLOAD['imglnk']
            )
            created = True
    PAYLOAD = {'created': created}

    return render(request, 'save.html', {'payload': PAYLOAD})


def selectMovie(request, moviename):
    movie_object = Movie.objects.get(moviename=moviename)
    # PAYLOAD STRUCTURE ==  {'scraped_data': scraped_data, 'query': query, 'imglnk': imglnk}
    PAYLOAD = fetch_from_db(movie_object)

    return render(request, 'progress.html', {'payload': PAYLOAD})


def myScrapes(request):
    # payload has been coded into the template
    return render(request, 'personal_scrapes.html')


# special function to fetch data from database
def fetch_from_db(movie_object):
    '''
        parameter: a movie object from django.models
        manipulation: fetches the movie object details and parse them into a dictionary format
        return: returns a dictionary object with the elements of the movie object organized in the format: 
                {'scraped_data':<something>, 'imglnk':<something>, 'scraped':<something>}
    '''

    movielink = movie_object.movielink.split(',')
    scraped_data = {movie_object.moviename: movielink}
    PAYLOAD = {
        'scraped_data': scraped_data,
        'imglnk': movie_object.imagelink,
        'scraped': False,
    }
    return PAYLOAD
