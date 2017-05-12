import markovify
import urllib.request
import json
import lyricwikia
import sys
import poetrytools
import time


logo = """===========================================================================
\033[1m
    ___ _                   _
   / __) |                 (_)  _
 _| |__| | ___  _ _ _  ____ _ _| |_ _____  ____
(_   __) |/ _ \| | | |/ ___) (_   _) ___ |/ ___)
  | |  | | |_| | | | | |   | | | |_| ____| |
  |_|   \_)___/ \___/|_|   |_|  \__)_____)_|


By Richard Farman\033[0m
Written in \033[93mPython3\033[0m with \033[94mMusicGraph\033[0m, \033[92mlyricswikia\033[0m, \033[91mmarkovify\033[0m, and \033[1;36mpoetrytools\033[0m
==========================================================================="""

api_key = None

try:
    f = open('API_KEY', 'r')
    api_key = f.read().replace('\n', '')
except:
    pass



genres = """Alternative/Indie
Blues
Cast Recordings/Cabaret
Christian/Gospel
Children's
Classical/Opera
Comedy/Spoken Word
Country
Electronica/Dance
Folk
Instrumental
Jazz
Latin
New Age
Pop
Rap/Hip Hop
Reggae/Ska
Rock
Seasonal
Soul/R&B
Soundtracks
Vocals
World""".lower().rstrip().replace(' ', '+').split('\n')

decades = """1890s
1900s
1910s
1920s
1930s
1940s
1950s
1960s
1970s
1980s
1990s
2000s
2010s
""".rstrip().split('\n')

yes_words = ['y', 'ye', 'yea', 'yee', 'yes', 'yeah', 'yup']
no_words = ['n', 'no', 'nop', 'nope', 'nah', 'nay']

model_types = ['artist', 'album', 'genres', 'decades']

def get_model_type():
    while True:
        print("\033[1mWould you like to model by artist, album, genres, or decades?\033[0m")
        model_type = input('> ').lower().rstrip()
        if model_type in model_types:
            break
#        if model == 'track':
#            base = 'http://api.musicgraph.com/api/v2/track/'
#            break
    return model_type


def get_tag(model_type):
    valid = True
    while valid:
        print("\033[1mEnter the name of the", model_type, "that you would like to model:\033[0m")
        if model_type == 'genres':
            print(genres)
        elif model_type == 'decades':
            print(decades)
        tag = input('> ').lower().rstrip().replace(' ', '+')
        if model_type == 'genres':
            if tag in genres:
                break
        elif model_type == 'decades':
            if tag in decades:
                break
        elif tag:
            break
    return tag


def get_limit():
    while True:
        print("\033[1mHow many tracks would you like to model? [1-100]\033[0m")
        limit = input('> ')
        try:
            if int(limit) > 0 and int(limit) < 101:
                break
        except Exception as e:
            continue
    return limit


def get_playlist(model_type, tag, limit):
    tracks = {}
    base_url = 'http://api.musicgraph.com/api/v2/playlist'
    api_url = '?api_key=' + api_key
    search_url = '&' + model_type + '=' + tag + '&limit=' + limit
    tracks_url = base_url + api_url + search_url
    tracks_request = urllib.request.urlopen(tracks_url).read().decode('utf-8')
    track_data = json.loads(tracks_request)
    for i in track_data['data']:
        title = i['title']
        artist_name = i['artist_name']
        if artist_name in tracks.keys():
            tracks[artist_name].append(title)
        else:
            tracks[artist_name] = [title]
    return tracks


def get_tracks(model_type, tag, limit):
    tracks = {}
    base_url = 'http://api.musicgraph.com/api/v2/' + model_type + '/'
    api_url = 'suggest?api_key=' + api_key
    search_url = '&prefix=' + tag + '&limit=1'
    request_url = base_url + api_url + search_url
    response = urllib.request.urlopen(request_url).read().decode('utf-8')
    response_data = json.loads(response)
    response_id = response_data['data'][0]['id']
    limit_url = '&limit=' + limit
    response_url = response_id + '/tracks?api_key=' + api_key + limit_url
    tracks_url = base_url + response_url
    tracks_request = urllib.request.urlopen(tracks_url).read().decode('utf-8')
    tracks_data = json.loads(tracks_request)
    for i in tracks_data['data']:
        title = i['title']
        artist_name = i['artist_name']
        if artist_name in tracks.keys():
            if title not in tracks[artist_name]:
                tracks[artist_name].append(title)
        else:
            tracks[artist_name] = [title]
    return tracks


# Searching playlist by track is currently broken on MusicGraph
# def get_track_tracks(base, model, tag):
#     data = {}
#     track_request_url = base + 'suggest?api_key=' + api_key + '&prefix=' + tag + '&limit=1'
#     print(track_request_url)
#     track = urllib.request.urlopen(track_request_url).read().decode('utf-8')
#     track_data = json.loads(track)
#     track_id = track_data['data'][0]['id']
#     playlist_url = 'http://api.musicgraph.com/api/v2/playlist'
#     playlist_request_url = playlist_url + '?api_key=' + api_key + '&' + model + '=' + '95d46167-20d3-1612-7960-d54f15c7961c'
#     print(playlist_request_url)
#     print('http://api.musicgraph.com/api/v2/playlist?api_key=c8303e90962e3a5ebd5a1f260a69b138&track_ids=95d46167-20d3-1612-7960-d54f15c7961c')
#     playlist = urllib.request.urlopen(playlist_request_url).read().decode('utf-8')
#     playlist_data = json.loads(playlist)
#     print(playlist_data)
#     for i in playlist_data['data']:
#         title = i['title']
#         artist_name = i['artist_name']
#         if artist_name in data.keys():
#             data[artist_name].append(title)
#         else:
#             data[artist_name] = [title]
#     return data


def generate_lyrics(source):
    lyrics = []
    artists = []
    titles = []
    for artist in source:
        track_list = source[artist]
        for track in track_list:
            try:
                lyric = lyricwikia.get_lyrics(artist, track).rstrip()
                lyrics.append(lyric)
                titles.append(track)
                if artist not in artists:
                    artist.append(artist)
            except Exception:
                continue
    return lyrics, artists, titles


# This doesn't work
# def generate_title(titles):
#     title_list = '\n'.join(titles).rstrip()
#     print(title_list)
#     title_model = markovify.NewlineText(title_list)
#     while True:
#         markov_title = title_model.make_sentence(test_ouput=False)
#         print(markov_title)
#         if markov_title is not None:
#             break
#     print(markov_title)


# This doesn't work
# def generate_artist(artists):
#     artist_list = '\n'.join(artists).rstrip()
#     print(artist_list)
#     artist_model = markovify.NewlineText(artist_list)
#     while True:
#         markov_artist = artist_model.make_sentence(tries=100, test_ouput=False)
#         if markov_artist is not None:
#             break
#     print(markov_artist)


def generate_model(source):
    model_list = []
    for lyric in source:
        lyric_model = markovify.NewlineText(lyric)
        model_list.append(lyric_model)
    try:
        model_combo = markovify.combine(model_list)
    except ValueError as e:
        print(e)
        sys.exit()
    return model_combo


def generate_flow(model):
    lyric_list = []
    while len(lyric_list) < 4:
        sentence = model.make_sentence()
        if sentence is not None:
            lyric_list.append(sentence)
    return lyric_list


def generate_rhyme_dict(model, rhyme_dict):
    timeout = time.time() + 30
    timeout_limit = 0
    dict_length = 0
    while True:
        if (len(rhyme_dict) == dict_length):
            timeout_limit += 1
        else:
            timeout_limit = 0
        dict_length = len(rhyme_dict)
        sentence = model.make_short_sentence(70)
        if sentence is not None:
            rhyme = sentence.split()[-1]
            if rhyme in rhyme_dict.keys():
                if sentence not in rhyme_dict[rhyme]:
                    rhyme_dict[rhyme].append(sentence)
            else:
                rhyme_dict[rhyme] = [sentence]

        if time.time() > timeout or timeout_limit > 1000:
            break
    return rhyme_dict


def levenshtein_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def generate_bar(model, rhyme_dict):
    timeout = time.time() + 5
    while True:
        sentence = model.make_short_sentence(70)
        best_match = ''
        distance = float('inf')
        if sentence is not None:
            rhyme = sentence.split()[-1]
            token_sentence = poetrytools.tokenize(sentence)
            metrical_scheme, num_lines, line_lengths, metre = poetrytools.guess_metre(token_sentence)
            for key in rhyme_dict.keys():
                if key.lower() != rhyme.lower() and poetrytools.rhymes(rhyme, key):
                    sentence_list = rhyme_dict[key]
                    for sentence2 in sentence_list:
                        token_sentence2 = poetrytools.tokenize(sentence2)
                        metrical_scheme2, num_lines2, line_lengths2, metre2 = poetrytools.guess_metre(token_sentence2)
                        if levenshtein_distance(metrical_scheme[0], metrical_scheme2[0]) < distance:
                            distance = levenshtein_distance(metrical_scheme[0], metrical_scheme2[0])
                            best_match = sentence2
        if best_match != '':
            return sentence + '\n' + best_match.strip() + '\n'
        if time.time() > timeout:
            break

def get_model():
    model_type = get_model_type()
    tag = get_tag(model_type)
    limit = get_limit()
    print('\033[1mGetting tracks by', model_type, 'for', tag + '...\033[0m')
    if model_type in ['artist', 'album']:
        source = get_tracks(model_type, tag, limit)
    elif model_type in ['genres', 'decades']:
        source = get_playlist(model_type, tag, limit)
    print("\033[1mGetting lyrics for tracks...")
    lyrics, artists, titles = generate_lyrics(source)
    print("\033[1mGenerating models for tracks...\033[0m")
    model = generate_model(lyrics)
    return model


def generate_verse(model, rhyme_dict):
    verse = ''
    for i in range(2):
        verse += generate_bar(model, rhyme_dict)
    return verse


def generate_chorus(model, rhyme_dict):
    chorus = ''
    for i in range(2):
        bar = generate_bar(model, rhyme_dict)
        if bar is not None:
            chorus += bar
    if chorus:
        return chorus
    else:
        return "\033[1mYour rhyme dictionary size (" + str(len(rhyme_dict)) + ") is not enough to generate a bar\033[0m"


def flowriter():
    if len(sys.argv) > 1:
        try:
            print("\033[1mGetting model from " + sys.argv[1] + "...\033[0m")
            f = open(sys.argv[1], 'r')
            model_json = json.load(f)
            model = markovify.NewlineText.from_json(
                model_json
            )
            if len(sys.argv) == 3 and sys.argv[2] == 'edit':
                model = markovify.combine(
                    [model, get_model()]
                )
                model_json = model.to_json()
                print("\033[1mSaving model to " + sys.argv[1] + "...\033[0m")
                with open(sys.argv[1], 'w') as f:
                    json.dump(model_json, f)
        except (IOError, OSError) as e:
            print(e)
            model = get_model()
            model_json = model.to_json()
            print("\033[1mSaving model to " + sys.argv[1] + "\033[0m")
            with open(sys.argv[1], 'w') as f:
                json.dump(model_json, f)
        print("\033[1mGenerating a rhyme dictionary...\033[0m")
        try:
            f = open(sys.argv[1].split('.')[0] + '_rhyme.json', 'r')
            rhyme_dict = generate_rhyme_dict(model, json.load(f))
        except (IOError, OSError) as e:
            rhyme_dict = generate_rhyme_dict(model, {})
        with open(sys.argv[1].split('.')[0] + '_rhyme.json', 'w') as f:
            json.dump(rhyme_dict, f)
    else:
        model = get_model()
        print("\033[1mGenerating rhyme dictionary...\033[0m")
        rhyme_dict = generate_rhyme_dict(model, {})
    # print("Generating markov flow...")
    # flow = generate_flow(model)
    print("\033[1mGenerating verses from rhyme dictionary...\033[0m")
    while True:
        print("---------------------------------------------------------------------------")
        print('')
        chorus = generate_chorus(model, rhyme_dict)
        # print('\n')
        # for i in range(2):
        #     print(generate_verse(model, rhyme_dict))
        # print(chorus)
        # for i in range(2):
        #     print(generate_verse(model, rhyme_dict))
        print(chorus)
        print("---------------------------------------------------------------------------")
        while True:
            print("\033[1mWould you like to generate another verse? [y/n]\033[0m")
            response = input('> ')
            if response in yes_words + no_words:
                break
        if response in no_words:
            break


def main():
    print(logo)
    if api_key is None:
        print("Missing API_KEY file with valid MusicGraph API key")
        sys.exit()
    while True:
        flowriter()
        while True:
            print("\033[1mWould you like to continue? [y/n]\033[0m")
            response = input('> ')
            if response in yes_words + no_words:
                break
        if response in no_words:
            break


if __name__ == '__main__':
    main()
