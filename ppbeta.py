import feedparser
import requests
import curses
import re

import colorama
import datetime
import os
import shutil
import sys
import urllib
import argparse
import progressbar
from mutagen.id3 import ID3, TALB, TIT2, TDRC, TCON, COMM, ID3NoHeaderError


podcast_list = [
        'YouMustRememberThis https://feeds.megaphone.fm/YMRT7068253588',
        'escapepod https://escapepod.org/feed/podcast/',
        'radiolab https://feeds.simplecast.com/EmVW7VGp',
        'ThisAmericanLife https://www.thisamericanlife.org/podcast/rss.xml',
        '500songs https://500songs.com/feed/podcast/a-history-of-rock-music-in-500-songs'
        ]


def list_selector(items):
    """
    Creates an interactive selector from a list using curses.

    Args:
        items (list): List of items to select from

    Returns:
        any: The selected item from the list

    Usage:
        selected = list_selector(['apple', 'banana', 'orange'])
    """
    def show_menu(stdscr, selected_idx):
        # Clear screen
        stdscr.clear()

        # Get screen height and width
        height, width = stdscr.getmaxyx()

        # Calculate center of screen
        start_y = max(0, (height - len(items)) // 2)
        start_x = max(0, (width - max(len(str(item)) for item in items)) // 2)

        # Display title
        title = "Select an item (use arrow keys, press Enter to select)"
        stdscr.addstr(start_y - 2, max(0, (width - len(title)) // 2), title)

        # Display all items
        for idx, item in enumerate(items):
            # Highlight selected item
            if idx == selected_idx:
                attr = curses.A_REVERSE
            else:
                attr = curses.A_NORMAL

            # Display item
            stdscr.addstr(start_y + idx, start_x, str(item), attr)

        # Refresh screen
        stdscr.refresh()

    def selector(stdscr):
        # Hide cursor
        curses.curs_set(0)

        # Initialize selection
        current_idx = 0

        # Display initial menu
        show_menu(stdscr, current_idx)

        while True:
            # Get user input
            key = stdscr.getch()

            if key == curses.KEY_UP and current_idx > 0:
                current_idx -= 1
            elif key == curses.KEY_DOWN and current_idx < len(items) - 1:
                current_idx += 1
            elif key == 10:  # Enter key
                return items[current_idx]

            # Update display
            show_menu(stdscr, current_idx)

    # Handle empty list
    if not items:
        return None

    # Run selector in curses wrapper
    return curses.wrapper(selector)


def download_feed(url, podname):
    filename = f'{podname}.rss'
    response = requests.get(url)
    total_size = len(response.content)
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                '''
                progress = int(f.tell() * 100 / total_size)
                print(f'Downloading: {progress}%', end=' ', flush=True)
                print('Download complete!')
                '''


def read_feed(podname):
    filename = f'{podname}.rss'
    with open(filename, 'r') as file:
        data = file.read()
        return data


def fetch_podcast_info(rss_feed, parsed_feed):
    # Parse the RSS feed
    feed = feedparser.parse(rss_feed)

    # Check if the feed is valid
    if feed.bozo:
        print('Error parsing feed.')
        return

    # Print and write the podcast title
    with open(parsed_feed, 'w') as f:
        print(f'Podcast Title: {feed.feed.title}')
        f.write(f'Podcast Title: {feed.feed.title}\n')

        # Iterate through each episode in the feed
        for entry in feed.entries:
            name = entry.title
            description = entry.description
            download_url = (
                entry.enclosure['url']
                if 'enclosure' in entry
                else 'No download URL available')

            # Print formatted information
            print('+' * 79)
            f.write('+' * 79 + '\n')
            print(f'Episode Name: \' {entry.title} \'')
            f.write(f'Episode Name: " {entry.title} "\n')
            print(f'Description:')
            f.write(f'Description:\n')
            print('\t', f'{entry.description}')
            f.write(f'\t{entry.description}\n')
            print(f'Enclosure URL:')
            f.write(f'Enclosure URL:\n')
            i = 0
            for k in entry['links']:
                href = entry['links'][i]['href']
                if href.endswith('.mp3'):
                    download_url = href
                print(i, '->', entry['links'][i]['href'])
                f.write(f'{i}  ->  {entry['links'][i]['href']}\n')
                i += 1
            print(f'Download URL:')
            f.write(f'Download URL:\n')
            print('\t', f'{download_url}')
            f.write(f'\t{download_url}\n')
            with open(f'{feed.feed.title}_mp3.txt', 'a') as mp3:
                mp3.write(f'{download_url}\n')

            remove_duplicates(f'{feed.feed.title}_mp3.txt')


def create_selector(stdscr, options):

    current_row = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        for i, option in enumerate(options):
            x = w//2 - len(option)//2
            y = h//2 - len(options)//2 + i
            if i == current_row:
                stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(y, x, option)
            stdscr.attroff(curses.A_REVERSE)

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_row = max(0, current_row - 1)
        elif key == curses.KEY_DOWN:
            current_row = min(len(options) - 1, current_row + 1)
        elif key == ord('\n'):
            return options[current_row]


def remove_duplicates(filename):

    lines = []
    with open(filename, 'r') as f:
        for line in f:
            if line not in lines:
                lines.append(line)

    with open(filename, 'w') as f:
        for line in lines:
            f.write(line)


def main(stdscr):
    options = [
            'YouMustRememberThis https://feeds.megaphone.fm/YMRT7068253588',
            'escapepod https://escapepod.org/feed/podcast/',
            'radiolab https://feeds.simplecast.com/EmVW7VGp',
            'ThisAmericanLife https://www.thisamericanlife.org/podcast/rss.xml',
            '500songs https://500songs.com/feed/podcast/a-history-of-rock-music-in-500-songs'
            ]
    choice = create_selector(stdscr, options)
    stdscr.addstr(0, 0, f'You selected: {choice}')
    stdscr.getch()
    selected_url = choice
    pod_title = re.split(" ", selected_url)[0]
    rss_url = re.split(" ", selected_url)[-1]


'''
print(' pod_title= ', pod_title, ' rss_url=', rss_url)
podname = re.split('\\.', rss_url)
print('podname=',podname)
podname = re.split('\\/', podname[0])
print('podname=',podname)
podname = podname[-1]
print(pod_title, 'end of line')
'''


podname = re.split('\\.', rss_url)
podname = re.split('\\/', podname[0])
podname = podname[-1]
download_feed(rss_url, podname)
feed = read_feed(podname)
parsed_feed = fetch_podcast_info(feed)


# pod.py
__version__ = 2.0
__updated__ = 20161125


class pcodes:
    BOLD = colorama.Style.BRIGHT
    DIM = colorama.Style.DIM
    ERROR = colorama.Style.BRIGHT + colorama.Fore.RED
    DESC = colorama.Style.BRIGHT + colorama.Fore.MAGENTA
    DOTPOD = colorama.Style.BRIGHT + colorama.Fore.BLUE
    PUBDATE = colorama.Style.BRIGHT + colorama.Fore.GREEN
    EPISODE = colorama.Style.BRIGHT + colorama.Fore.CYAN
    FILE = colorama.Style.BRIGHT + colorama.Fore.YELLOW
    URL = colorama.Style.BRIGHT + colorama.Fore.WHITE
    END = colorama.Style.RESET_ALL + colorama.Fore.RESET


def pod_error(pod):
    title = 'error in {}{}{}.'.format(pcodes.DOTPOD, pod['title'], pcodes.END)
    for error in pod['error']:
        e, message = error
        message = pcodes.ERROR + message + pcodes.END
        print('{} | {}\n  {}'.format(title, str(e), message))


def get_selected_pod_list(podcast_home, pod_list):
    pods = []
    for pod_dir in pod_list:
        pod = {}
        pod['dir'] = os.path.join(podcast_home, pod_dir)
        pod['db'] = os.path.join(podcast_home, pod_dir, 'db')
        pod['epis'] = os.path.join(podcast_home, pod_dir, 'epis')
        pod['log'] = os.path.join(podcast_home, pod_dir, 'log')
        pod['rss'] = os.path.join(podcast_home, pod_dir, 'rss')
        pod['title'] = pod_dir[:-4]
        pod['url'] = os.path.join(podcast_home, pod_dir, 'url')
        pod['pickle'] = os.path.join(podcast_home, pod_dir, 'pickle')
        pod['error'] = []

        for i in ['db', 'epis', 'log', 'rss', 'url']:
            if not os.path.isfile(pod[i]):
                exit(
                    'error: .pod {}{}{} does not include {}{}{}'.format(
                        pcodes.DOTPOD, pod_dir,
                        pcodes.END, pcodes.FILE, pod[i], pcodes.END))

        pods.append(pod)
    return pods


def get_pod_list(podcast_home):
    pods = []
    for pod_dir in os.listdir(podcast_home):
        if pod_dir.endswith('.pod'):
            pod = {}
            pod['dir'] = os.path.join(podcast_home, pod_dir)
            pod['db'] = os.path.join(podcast_home, pod_dir, 'db')
            pod['epis'] = os.path.join(podcast_home, pod_dir, 'epis')
            pod['log'] = os.path.join(podcast_home, pod_dir, 'log')
            pod['rss'] = os.path.join(podcast_home, pod_dir, 'rss')
            pod['title'] = pod_dir[:-4]
            pod['url'] = os.path.join(podcast_home, pod_dir, 'url')
            pod['pickle'] = os.path.join(podcast_home, pod_dir, 'pickle')
            pod['error'] = []

            for i in ['db', 'epis', 'log', 'rss', 'url']:
                if not os.path.isfile(pod[i]):
                    pod['error'].append((
                        IOError, 'file not found: "{}".'.format(
                            os.path.basename(pod[i]))))
                    pod_error(pod)

            pods.append(pod)
    return pods


def get_updated(pod):
    # pubDate_str = 'Mon, 31 Dec 2099 ...'
    # updated_str = 'updated: 20991231'
    with open(pod['log'], 'r') as log:
        lines = log.readlines()

    count = len(lines) - 1
    if count < 1:
        update_line = 'rss updated: {}\n'.format('unknown')
    else:
        while count:
            update_line = lines[count]
            if 'rss updated: ' in update_line:
                break
            count -= 1

    count = len(lines) - 1
    if count < 1:
        download_line = 'download: {}\n'.format('unknown')
    else:
        while count:
            download_line = lines[count]
            if 'download: ' in update_line:
                break
            count -= 1

    if 'rss updated: ' not in update_line:
        update_line = ' unknown'
    if 'download: ' not in download_line:
        download_line = ' unknown'

    # return date in format YYYYMMDD:
    return update_line.split()[-1].rstrip(), download_line.split()[-1].rstrip()


def get_new_episodes(pod):
    updated, downloaded = get_updated(pod)
    # print(' rss last updated: {}{}{} last download: {}{}{}'.format(
    #       pcodes.PUBDATE, updated, pcodes.END,
    #       pcodes.PUBDATE, updated, pcodes.END))

    # load db
    try:
        if pod['title'] == 'starshipsofa':
            db = open(pod['db'], 'r').read().replace(
                'media.mp3', '').splitlines()
        else:
            db = open(pod['db'], 'r').read().splitlines()
    except Exception as e:
        print('{}error{} in {}{}{}\n  failed to read db file. {}\n  {}{}{}'.
              format(pcodes.ERROR,
                     pcodes.END,
                     pcodes.DOTPOD,
                     pod['title'],
                     pcodes.END,
                     url.rstrip(),
                     pcodes.DESC,
                     str(e),
                     pcodes.END))
        return []
    # load url
    with open(pod['url'], 'r') as f:
        url = f.read()
    # download new rss
    try:
        rss_file, headers = urllib.urlretrieve(url, pod['rss'])
    except Exception as e:
        print('{}error{} in {}{}{}\n  failed to download rss. {}\n  {}{}{}'.
              format(pcodes.ERROR,
                     pcodes.END,
                     pcodes.DOTPOD,
                     pod['title'],
                     pcodes.END,
                     url.rstrip(),
                     pcodes.DESC,
                     str(e),
                     pcodes.END))
        return []
    # read rss
    with open(pod['rss'], 'r') as f:
        rss = f.read()

    parsed_rss = feedparser.parse(rss)
    episodes = []
    for entry in parsed_rss.entries:
        try:
            if entry.enclosures and entry.enclosures[0].href:
                episodes.append(entry)
        except Exception as e:
            print('{}error{} in episode rss\n  {}'.format(
                pcodes.ERROR, pcodes.END, str(e)))

    new_episodes = []
    for episode in episodes:
        url = episode.enclosures[0].href
        url_file = url.split('/')[-1]
        title = episode.title.replace(' ', '_').format(
            'ascii', 'ignore')
        title = title.replace('/', '-')
        title = title.replace(':', '-')

        if 'id' in episode.keys():
            id_string = episode.id
        else:
            id_string = title

        if url_file not in db:
            if title not in db:
                if id_string not in db:
                    new_episodes.append(episode)

    # update log
    with open(pod['log'], 'a') as log:
        log.write('rss updated: {}\n'.format(
            datetime.date.today().strftime('%Y%m%d')))

    return new_episodes


def download_episode(pod, episode, progress=False):
    def progress_bar_retrieve(url, file_path):
        widgets = [' ', progressbar.Percentage(), ' ',
                   progressbar.Bar(marker=progressbar.RotatingMarker()), ' ',
                   progressbar.ETA(),
                   ' ',
                   progressbar.FileTransferSpeed()]
        pbar = progressbar.ProgressBar(widgets=widgets)
        (f, h) = (None, None)

        def dlProgress(count, block_size, total_size):
            if pbar.maxval is None:
                pbar.maxval = total_size
                pbar.start()

            pbar.update(min(count * block_size, total_size))
        try:
            (f, h) = urllib.urlretrieve(url, file_path, reporthook=dlProgress)
            pbar.finish()
        except Exception as e:
            # traceback.print_exc(file=sys.stdout)
            print(u'{}error{} downloading {}{}{}\n  {}{}{}'.format(
                    pcodes.ERROR, pcodes.END, pcodes.FILE, file_path,
                    pcodes.END, pcodes.DESC, str(e), pcodes.END))
            file_path = None

        return (f, h)

    def no_progress_bar_retrieve(url, file_path):
        (f, h) = (None, None)
        try:
            (f, h) = urllib.urlretrieve(url, file_path)
        except Exception as e:
            print(u'{}error{} downloading {}{}{}\n  {}{}{}'.
                  format(pcodes.ERROR,
                         pcodes.END,
                         pcodes.FILE,
                         file_path,
                         pcodes.END,
                         pcodes.DESC,
                         str(e),
                         pcodes.END))
            file_path = None

        return (f, h)

    url = episode.enclosures[0].href
    url_file = os.path.basename(url)
    file_path = os.path.join(pod['dir'], url_file)
    # progress = True # pod.py
    if progress:
        (f, h) = progress_bar_retrieve(url, file_path)
    else:
        (f, h) = no_progress_bar_retrieve(url, file_path)

    if not h:
        print('Trying wget...')
        import subprocess
        subprocess.check_output(['wget', '--output-document={}'.
                                 format(file_path), url])

    return file_path


def tag_and_rename(pod, episode, file_path):

    # pubDate='Sun, 31 Dec 2099 23:59:59 -0800'

    published_pieces = episode.published.split()[1:4]
    date_obj = datetime.datetime.strptime(
        '{} {} {}'.format(*published_pieces), '%d %b %Y')
    published = date_obj.strftime('%Y%m%d')

    title = episode.title.replace(' ', '_')
    title = title.replace('/', '').encode('ascii', 'ignore')
    title = title.replace(':', '-')
    title = title.replace('"', '')
    title = title.replace('?', '')

    desc = u'"{}"'.format(episode.description)

    url = episode.enclosures[0].href

    filename = os.path.basename(file_path)

    # new_filename -> published-title.mp3
    new_filename = u'{}-{}.mp3'.format(published, title)

    # tag episode
    try:
        eid3 = ID3(file_path)
    except ID3NoHeaderError as e:
        eid3 = ID3()

    eid3.add(TALB(encoding=3, text=pod['title']))
    eid3.add(TIT2(encoding=3, text=title))
    eid3.add(TDRC(encoding=3, text=published[:4]))
    eid3.add(TCON(encoding=3, text=u'Podcast'))
    eid3.add(COMM(encoding=3, lang='ENG', desc=u'desc', text=desc))
    eid3.add(COMM(encoding=3, desc=u'file', text=filename))

    eid3.save(file_path, v1=2)

    # rename downloaded file
    shutil.move(file_path, os.path.join(pod['dir'], new_filename))

    return new_filename


def log_episode(pod, episode, filename):
    '''
    /db
    /log
    /episode
    /pickle
    '''
    published_pieces = episode.published.split()[1:4]
    date_obj = datetime.datetime.strptime(
        '{} {} {}'.format(*published_pieces), '%d %b %Y')
    published = date_obj.strftime('%Y%m%d')

    if 'id' in episode.keys():
        episode['id'] = episode.id
    else:
        episode['id'] = episode.title

    epidict = {'pub': published,
               'title': u'{}'.format(episode.title),
               'desc': u'"{}"'.format(
                episode.description.replace('\n', '<br />')),
               'url': episode.enclosures[0].href,
               'file': filename,
               'id': episode.id}

    with open(pod['epis'], 'a') as epis:
        epis.write(u'PUB={} TITLE={} DESC={} URL={} FILE={}\n'.format(
            epidict['pub'], epidict['title'], epidict['desc'], epidict['url'],
            os.path.basename(epidict['file'])).encode(
                'ascii', 'ignore'))

    with open(pod['pickle'], 'ab') as p:
        pickle.dump(epidict, p)

    with open(pod['db'], 'a') as db:
        title = epidict['title'].replace(' ', '_')
        title = title.replace('/', '-').encode('ascii', 'ignore')
        title = title.replace(':', '-')
        db.write(u'{}\n'.format(os.path.basename(epidict['url'])))
        db.write(u'{}\n'.format(title))
        db.write('{}\n'.format(epidict['id']))

    with open(pod['log'], 'a') as log:
        log.write('download: {}\n'.format(published))

    return epidict


def dotpod_start(podcast_dir):
    # if __name__ == "__main__":
    colorama.init()
    program_name = os.path.basename(sys.argv[0])
    program_version = "v{}".format(__version__)
    program_build_date = str(__updated__)
    program_version_message = "{} ({})".format(
        program_version, program_build_date)
    program_shortdesc = "%(prog)s: Archive Podcasts Automatically"
    program_license = "Free"

    # set podcast_home
    podcast_home = os.environ.get('PODCASTS')
    if not podcast_home:
        podcast_home = os.environ.get('PODCAST_HOME')
    if not podcast_home:
        podcast_home = podcast_dir
    if not os.path.isdir(podcast_home):
        exit(' pod directory {} cannot be read.'.format(podcast_home))

    '''Command line options'''
    parser = argparse.ArgumentParser(
        description=program_license,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '-d', '--dir', dest='podcast_home', action='store',
        default=podcast_home,
        help='PODCAST_HOME directory. [default: %(default)s]')
    parser.add_argument(
        '-p', '--pod', dest='podcast_home', action='store',
        default=podcast_home,
        help='PODCAST_HOME directory. [default: %(default)s]')
    parser.add_argument(
        "-q", "--quiet", action="store_true",
        help='no progress bar - use with cron [default: %(default)s]')
    parser.add_argument(
        "-c", "--cron", action="store_true",
        help="no progress bar - use with cron [default: %(default)s]")
    parser.add_argument(
        'dotpods', nargs='*', metavar='dotpod[.pod]',
        default=[], help='list of dotpods. [default: %(default)s]')

    # Process arguments
    args = parser.parse_args()
    if args.quiet:
        progress = False
    elif args.cron:
        progress = False
    else:
        progress = True

    if args.podcast_home:
        podcast_home = args.podcast_home

    dotpods = args.dotpods

    # load pods
    if len(dotpods) > 0:
        selected_pods = []
        for pod in dotpods:
            if not pod.endswith('.pod'):
                selected_pods.append(pod + '.pod')
            else:
                selected_pods.append(pod)

        pods = get_selected_pod_list(podcast_home, selected_pods)

    else:

        pods = get_pod_list(podcast_home)

    # iterate pod in pods
    for pod in pods:
        if pod['error']:
            pod_error(pod)
            continue

        podname = pod['title']
        header = u'{}{}{}: '.format(pcodes.DOTPOD, podname, pcodes.END)

        if progress:
            print(
                header + '{} {}{}{}'.format(
                    '=' * (78 - len(header) - len(podname)),
                    pcodes.DOTPOD, podname, pcodes.END))
        else:
            print(
                header + '{} '.format('=' * (78 - len(header) - len(podname))))

        new_episodes = get_new_episodes(pod)
        new_episodes.reverse()

        if not new_episodes:
            print(header + 'no new episodes.')
        else:
            for episode in new_episodes:
                print(
                    header + 'new episode in {}{}{}'.format(
                        pcodes.DOTPOD, podname, pcodes.END))
                published = header + 'published: {}{}{}'.format(
                    pcodes.PUBDATE, episode.published, pcodes.END)
                title = header + u'title: {}"{}"{}'.format(
                    pcodes.EPISODE, episode.title, pcodes.END)
                description = header + u'desc: {}{}{}'.format(
                    pcodes.DESC, episode.description, pcodes.END)
                url = header + 'url: {}{}{}'.format(
                    pcodes.URL, episode.enclosures[0].href, pcodes.END)
                print(published)
                print(title.encode('ascii', 'ignore'))
                print(description.encode('ascii', 'backslashreplace'))
                print(url)

                # download
                downloaded_episode = download_episode(
                    pod, episode, progress=progress)

                if not downloaded_episode:
                    continue

                try:
                    new_filename = tag_and_rename(
                        pod, episode, downloaded_episode)
                except IOError as e:
                    print('{}error{} in {}{}{}\n failed to tag_and_rename episode. {}\n {}{}{}'.
                          format(pcodes.ERROR,
                                 pcodes.END,
                                 pcodes.DOTPOD,
                                 pod['title'],
                                 pcodes.END,
                                 url.rstrip(),
                                 pcodes.DESC,
                                 str(e),
                                 pcodes.END))
                    continue

                print(header + u'new tagged file: {}{}{}'.format(
                    pcodes.FILE, os.path.join(
                        pod['dir'], new_filename), pcodes.END))

                epidict = log_episode(pod, episode, new_filename)


# vim: set expandtab shiftwidth=4 tabstop=4 linebreak: #
