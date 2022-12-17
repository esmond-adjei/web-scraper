from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .scrapealgo import *
from .scrapeTools import IMDB

from .models import Movie, UserMovie
from .form import RegisterForm

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
    # try:
    #     movie_data = Movie.objects.all()
    # except:
    #     print("User not logged in, yet")  # This is not true as of 2022/12/11

    PAYLOAD = {'page_title': 'Scrape a movie'}
    return render(request, 'index.html', {'payload': PAYLOAD})


def progress(request):

    query = request.GET['query']
    # if query exists fetch from database else scrape online
    movie_obj_db = Movie.objects.filter(
        query=query) or Movie.objects.filter(moviename=query)
    if len(movie_obj_db) and 'rf::' not in query:   # rf:: if for forced query
        PAYLOAD = {'page_title': str(query)}
        PAYLOAD['imglnk'] = fetch_from_db(movie_obj_db[0])['imglnk']
        PAYLOAD['scraped_data'] = fetch_from_db(movie_obj_db[0])[
            'scraped_data']
        for movie_obj_index in range(1, len(movie_obj_db)):
            PAYLOAD['scraped_data'].update(fetch_from_db(
                movie_obj_db[movie_obj_index])['scraped_data'])

    else:
        if 'rf::' in query:     # remove fored query
            query = query[4:]
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
                   'query': query, 'imglnk': imglnk, 'scraped': True, 'page_title': str(query)}
        with open('tmp.json', 'w') as wf:
            json.dump(PAYLOAD, wf, indent=2)

    return render(request, 'progress.html', {'payload': PAYLOAD})


def save(request):

    with open('tmp.json') as rf:
        PAYLOAD = json.load(rf)

    created = False
    for movie, links in PAYLOAD['scraped_data'].items():
        # check if movie is present before saving it.
        # if not in global, then not in local
        if movie not in [movie.moviename for movie in Movie.objects.all()]:
            mov_obj = Movie.objects.create(
                query=PAYLOAD['query'],
                moviename=movie,
                movielink=", ".join(links),
                imagelink=PAYLOAD['imglnk']
            )

            UserMovie.objects.create(
                user_movie=mov_obj,
                username=request.user
            )
        # if not in local...
        elif movie not in [mov_obj.user_movie.moviename for mov_obj in request.user.usermovie_set.all()]:
            UserMovie.objects.create(
                user_movie=Movie.objects.get(moviename=movie),
                username=request.user
            )
            created = True
        else:       # then movie already exists in local as well.
            created = False

    PAYLOAD = {'created': created,
               'page_title': f"Results for {PAYLOAD['query']} saved"}

    return render(request, 'save.html', {'payload': PAYLOAD})


def selectMovie(request, moviename):
    movie_object = Movie.objects.get(moviename=moviename)
    # PAYLOAD STRUCTURE ==  {'scraped_data': scraped_data, 'query': query, 'imglnk': imglnk}
    PAYLOAD = fetch_from_db(movie_object)
    PAYLOAD['page_title'] = moviename
    return render(request, 'progress.html', {'payload': PAYLOAD})


def myScrapes(request):
    # payload has been coded into the template
    PAYLOAD = {}
    PAYLOAD['page_title'] = str(request.user.username) + "'s list"

    return render(request, 'personal_scrapes.html', {'payload': PAYLOAD})


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
