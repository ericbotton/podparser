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


def read_episodes_from_file(filename):
    """Reads lines from a file and returns a list of lines.

    Args:
        filename: The name of the file to read.

    Returns:
        A list of lines from the file.
    """

    with open(filename, 'r') as file:
        episode_list = file.readlines()

    return episode_list


def tag_and_rename(mp3_path):

    def print_mp3_metadata(file_path):
        """Prints the metadata of an MP3 file.

        Args:
            file_path: The path to the MP3 file.
        """

        audio = mutagen.File(file_path)

        print("Metadata for:", file_path)
        for key, value in audio.items():
            print(f"{key}: {value}")

    # Example usage:
    file_path = mp3_path
    metadata = mutagen.File(file_path)
    episode_title = metadata['TIT2']

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

    filename = os.path.basename(mp3_path)

    # new_filename -> published-title.mp3
    new_filename = u'{}-{}.`'.format(published, title)

    # tag episode
    try:
        eid3 = ID3(mp3_path)
    except ID3NoHeaderError as e:
        eid3 = ID3()

    eid3.add(TALB(encoding=3, text=pod['title']))
    eid3.add(TIT2(encoding=3, text=title))
    eid3.add(TDRC(encoding=3, text=published[:4]))
    eid3.add(TCON(encoding=3, text=u'Podcast'))
    eid3.add(COMM(encoding=3, lang='ENG', desc=u'desc', text=desc))
    eid3.add(COMM(encoding=3, desc=u'file', text=filename))

    eid3.save(mp3_path, v1=2)

    # rename downloaded file
    shutil.move(mp3_path, os.path.join(pod['dir'], new_filename))

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
    pod_directory = "/home/edb/Documents/Projects/podparser/"
    options = []
    for f in read_files_in_directory(pod_directory):
        if ".mp3.txt" in f:
            options.append(str(f))
    selected_option = select_from_list(options)
    print(f'selected_option = {selected_option}')
    episode_list = read_episodes_from_file(selected_option)
