import curses
import requests
import os
import mutagen

from tqdm import tqdm


def read_files_in_directory(directory_path):

    file_list = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(file_path)
    return file_list


def read_episodes_from_file(filename):
    with open(filename, 'r') as file:
        lines = [line.rstrip() for line in file]
    return lines


def download_file(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    with open(filename, 'wb') as f:
        for data in tqdm(response.iter_content(chunk_size=1024),
                         total=total_size,
                         unit='B',
                         unit_scale=True,
                         desc=filename):
            f.write(data)


def format_time_struct(time_struct):
    # Convert the struct_time object to a datetime object
    dt_object = datetime.datetime.fromtimestamp(time.mktime(time_struct))
    # Format the datetime object as an ISO 8601 string
    iso_formatted_time = dt_object.isoformat()
    return iso_formatted_time


def tag_and_rename(mp3_filename):

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

    filename = os.path.basename(mp3_filename)

    # new_filename -> published-title.mp3
    new_filename = u'{}-{}.`'.format(published, title)

    # tag episode
    try:
        eid3 = ID3(mp3_filename)
    except ID3NoHeaderError as e:
        eid3 = ID3()

    eid3.add(TALB(encoding=3, text=pod['title']))
    eid3.add(TIT2(encoding=3, text=title))
    eid3.add(TDRC(encoding=3, text=published[:4]))
    eid3.add(TCON(encoding=3, text=u'Podcast'))
    eid3.add(COMM(encoding=3, lang='ENG', desc=u'desc', text=desc))
    eid3.add(COMM(encoding=3, desc=u'file', text=filename))

    eid3.save(mp3_filename, v1=2)

    # rename downloaded file
    shutil.move(mp3_filename, os.path.join(pod['dir'], new_filename))

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
    podcast_directory = "/home/edb/Documents/Projects/podparser/"
    file_list = read_files_in_directory(podcast_directory)
    options = []
    for f in file_list:
        if '.mp3.txt' in f:
            options.append((f.split('/')[-1], f))
    selected_option = select_from_list(options)
    mp3_list_filename = selected_option[1]
    print(f'mp3_list_filename = {mp3_list_filename}')
    mp3_file_list_strings = read_episodes_from_file(mp3_list_filename)

    mp3_file_list = []
    for mp3 in mp3_file_list:
        mp3_file_title = mp3.split(' _|_ ')[0]
        mp3_file_url = mp3.split(' _|_ ')[1]
        print(mp3_file_title)
        print(mp3_file_url)
        mp3_file_list.append((mp3_file_title, mp3_file_url))

    print(mp3_file_list)
    # selected_episode = select_from_list(mp3_file_list)
    # print(f'selected_episode[0] = {selected_episode[0]}')
    # print(f'selected_episode[1] = {selected_episode[1]}')
