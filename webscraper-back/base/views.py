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
            imglnk = IMDB(query)
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

    for movie, links in PAYLOAD['scraped_data'].items():
        # 'get_or_create()' -> checks if not present then create, else get. But we use the get for nothing
        Movie.objects.get_or_create(
            query=PAYLOAD['query'],
            moviename=movie,
            movielink=", ".join(links),
            imagelink=PAYLOAD['imglnk']
        )

    return render(request, 'save.html')
