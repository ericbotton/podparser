#!/usr/bin/python
import curses
import feedparser
import requests
import time
import datetime

''' podcast list =[ (podcast title,
                    podcast url)
                    ]
'''
podcast_list = [
        ('You Must Remember This',
         'https://feeds.megaphone.fm/YMRT7068253588'),
        ('escapepod',
         'https://escapepod.org/feed/podcast/'),
        ('radiolab',
         'https://feeds.simplecast.com/EmVW7VGp'),
        ('This American Life',
         'https://www.thisamericanlife.org/podcast/rss.xml'),
        ('a-history-of-rock-music-in-500songs',
         'https://500songs.com/feed/podcast/\
             a-history-of-rock-music-in-500-songs'),
        ('City Lights (omnycontent.com)', 'https://www.omnycontent.com/\
            d/playlist/5ec71174-b7c1-46da-88de-b18e00b479cf/\
                59709110-36d6-4f15-9fcb-b216012865ef/\
                    c2912173-9add-43da-bdf6-b2160128660b/podcast.rss'),
        ('Crash Course Pods: The Universe',
            'https://feeds.simplecast.com/ASAdCBih'),
        ('Crucible Moments', 'https://feeds.megaphone.fm/VMP5587961509'),
        ('Dan Carlin\'s Hardcore History',
         'https://feeds.feedburner.com/dancarlin/history'),
        ('Dan Carlin\'s Hardcore History: Addendum',
         'https://dchhaddendum.libsyn.com/rss')
        ]
parsed_directory = '/home/edb/podparser/parsed/'


def download_feed(podcast_title, podcast_url):
    rss_file = f'{podcast_title}.feed.rss'
    response = requests.get(podcast_url)
    total_size = len(response.content)
    with open(rss_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                progress = int(f.tell() * 100 / total_size)
                print(f"Downloading: {progress}%", end=' ', flush=True)
                print("Download complete!")


def read_feed(filename):
    with open(filename, 'r') as file:
        data = file.read()
        return data


def format_time_struct(time_struct):
    # Convert the struct_time object to a datetime object
    dt_object = datetime.datetime.fromtimestamp(time.mktime(time_struct))
    # Format the datetime object as an ISO 8601 string
    iso_formatted_time = dt_object.isoformat()
    return iso_formatted_time


def fetch_podcast_info(rss_feed, parsed_file, mp3_file):
    # Parse the RSS feed
    feed = feedparser.parse(rss_feed)

    # Check if the feed is valid
    if feed.bozo:
        print("Error parsing feed.")
        return

    # Print and write the podcast title
    with open(parsed_file, 'w') as f:
        podcast_title = feed.feed.title
        print(f"Podcast Title: {podcast_title}")
        f.write(f'Podcast Title: "{podcast_title}"\n')

        # Iterate through each episode in the feed
        n = len(feed.entries)
        for entry in feed.entries:
            episode_name = f'{n}. entry.title'
            n = n - 1
            description = entry.description
            download_url = str(entry['links'][-1]['href'])
            published_date = format_time_struct(entry['published_parsed'])
            # Print formatted information
            print("+" * 79)
            f.write('+' * 79 + '\n')
            print(f"Episode Name: \' {episode_name} \'")
            f.write(f'Episode Name: " {episode_name} "\n')
            print(f"Description:")
            f.write(f'Description:\n')
            print('\tdatetime', f"{entry.description}")
            f.write(f'\t{entry.description}\n')
            print(f"Enclosure URL:")
            f.write(f'Enclosure URL:\n')
            print(f"Download URL:")
            f.write(f'Download URL:\n')
            print('\t', f"{download_url}")
            f.write(f'\t{download_url}\n')
            with open(mp3_file, 'a') as mp3:
                mp3.write(f'{podcast_title} ' +
                          f'{published_date}_-_' +
                          f'{episode_name} _|_ ' +
                          f'{download_url}\n')

            remove_duplicates(mp3_file)


def remove_duplicates(filename):

    lines = []
    with open(filename, 'r') as f:
        for line in f:
            if line not in lines:
                lines.append(line)

    with open(filename, 'w') as f:
        for line in lines:
            f.write(line)


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


def curses_selector(stdscr, options):
    # Configure curses settings
    curses.curs_set(0)  # Hide the cursor
    current_index = 0  # Track the currently selected option

    while True:
        stdscr.clear()  # Clear the screen before drawing

        # Display all options in the list
        for idx, option in enumerate(options):
            # Highlight the current selection
            if idx == current_index:
                stdscr.addstr(idx, 0, option[0], curses.A_REVERSE)
            else:
                stdscr.addstr(idx, 0, option[0])

        # Refresh screen to show the updated list with selection
        stdscr.refresh()

        # Get the user's key input
        key = stdscr.getch()

        # Handle up/down arrow keys
        if key == curses.KEY_UP and current_index > 0:
            current_index -= 1
        elif key == curses.KEY_DOWN and current_index < len(options) - 1:
            current_index += 1
        # Enter key to confirm selection
        elif key == ord('\n'):
            return options[current_index]


def select_from_list(options):
    # Initialize curses and call our selector within the curses context
    return curses.wrapper(curses_selector, options)


# Example usage:
if __name__ == "__main__":
    options = podcast_list
    selected_option = select_from_list(options)
    podcast_title = selected_option[0]
    podcast_url = selected_option[1]
    print(f" selected podcast: {podcast_title}")
    print(f" selected url    : {podcast_url}")
    rss_file = f'{parsed_directory}/{podcast_title}.feed.rss'
    parsed_file = f'{parsed_directory}/{podcast_title}.parsed.txt'
    mp3_file = f'{parsed_directory}/{podcast_title}.mp3.txt'
    download_feed(podcast_title, podcast_url)
    rss_data = read_feed(rss_file)
    fetch_podcast_info(rss_data, parsed_file, mp3_file)
