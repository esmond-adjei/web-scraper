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
    # - need to have a special function that searches query from database:: movie queries or movie names
    PAYLOAD = {'scraped_data': '', 'imglnk': '', 'movie_type': '',
               'query': query, 'page_title': query, 'is_local': False}
    movie_obj_db = Movie.objects.filter(
        query__icontains=query) or Movie.objects.filter(moviename__icontains=query)

    if 'rf::' not in query and len(movie_obj_db):   # rf:: if for forced query
        # core properties of payload
        first_obj = fetch_from_db(movie_obj_db[0])
        PAYLOAD['imglnk'] = first_obj['imglnk']
        PAYLOAD['scraped_data'] = first_obj['scraped_data']
        PAYLOAD['movie_type'] = first_obj['movie_type']

        # check if global movie is also local
        isLocal = {m.moviename for m in movie_obj_db}.difference(
            {m.user_movie.moviename for m in request.user.usermovie_set.all()})
        if isLocal:
            PAYLOAD['is_local'] = False
        else:
            PAYLOAD['is_local'] = True

        # fetch from database in desired format and create a merged desired format
        for index in range(1, len(movie_obj_db)):
            PAYLOAD['scraped_data'].update(fetch_from_db(
                movie_obj_db[index])['scraped_data'])

    else:
        if 'rf::' in query:     # remove fored query
            query = query[4:]
        movie_type = request.GET['movie-type']
        PAYLOAD['movie_type'] = movie_type
        # make address based on movie type

        # option to download image
        try:
            if query.strip().replace("+", "") == '':    # if query is empty, return nothing
                scraped_data = {}
            else:
                address, movieKeyword = getAddress(movie_type, query)
                scraped_data = recursiveScrape(
                    find_tag('a', scrape(address)), movieKeyword.lower())
            download_img = request.GET['download-img']
        except:
            scraped_data = {}
            download_img = ''

        print('='*50)
        if download_img == 'yes':
            try:
                imglnk = IMDB(query)
            except:
                print("COULD NOT OBTAIN IMAGE FILE")
                imglnk = '#'
        else:
            imglnk = '#'

        # clean scraped data. remove all empty links
        scraped_data = {k: v for k, v in scraped_data.items() if v}

        PAYLOAD.update({'scraped_data': scraped_data, 'query': query,
                        'imglnk': imglnk, 'movie_type': movie_type})

        # save to global database
        save_global_db(PAYLOAD=PAYLOAD)

    with open('tmp.json', 'w') as wf:
        json.dump(PAYLOAD, wf, indent=2)

    return render(request, 'progress.html', {'payload': PAYLOAD})


def save(request):

    with open('tmp.json') as rf:
        PAYLOAD = json.load(rf)

    is_created = False
    # get movie from global database and save to local
    # check if movie exist locally before attempting to save
    payload_data = {mv for mv in PAYLOAD['scraped_data'].keys()}
    user_data = {
        mv.user_movie.moviename for mv in request.user.usermovie_set.all()}
    payload_not_in_user_data = payload_data.difference(user_data)
    if payload_not_in_user_data:
        for movie in payload_not_in_user_data:
            UserMovie.objects.create(
                user_movie=Movie.objects.get(moviename=movie),
                username=request.user
            )
            is_created = True
            print(">> SAVED LOCALLY")
    else:       # then movie already exists in local as well.
        is_created = False

    PAYLOAD = {'is_created': is_created,
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
                {'scraped_data':<something>, 'imglnk':<something>, 'is_local':<something>}
    '''

    movielink = movie_object.movielink.split(',')
    scraped_data = {movie_object.moviename: movielink}
    PAYLOAD = {
        'scraped_data': scraped_data,
        'imglnk': movie_object.imagelink,
        'movie_type': movie_object.movie_type,
    }
    return PAYLOAD


def save_global_db(PAYLOAD):
    if PAYLOAD['scraped_data']:
        for movie, links in PAYLOAD['scraped_data'].items():
            # check if movie is present before saving it.
            if movie not in [movie.moviename for movie in Movie.objects.all()]:
                Movie.objects.create(
                    query=PAYLOAD['query'],
                    moviename=movie,
                    movielink=", ".join(links),
                    imagelink=PAYLOAD['imglnk'],
                    movie_type=PAYLOAD['movie_type']
                )
