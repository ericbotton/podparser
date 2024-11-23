import curses
import os


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


def select_from_list(stdscr, options):
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)

    current_row = 0
    while True:
        stdscr.clear()
        for i, option in enumerate(options):
            if i == current_row:
                stdscr.attron(curses.color_pair(1))
            else:
                stdscr.attron(curses.color_pair(2))
            stdscr.addstr(i, 0, option)
        stdscr.attroff(curses.color_pair(1))
        stdscr.attroff(curses.color_pair(2))

        key = stdscr.getch()
        if key == curses.KEY_UP:
            current_row = max(0, current_row - 1)
        elif key == curses.KEY_DOWN:
            current_row = min(len(options) - 1, current_row + 1)
        elif key == curses.KEY_ENTER or key == ord('\n'):
            selected_item = options[current_row]
            print(f"selected item: {selected_item}")
            break
        elif key == ord('q'):
            break

        stdscr.refresh()

    return selected_item


def scrollable_list(items, max_visible=17):
    """
    Args:
      items: A list of items to display.
      max_visible: The maximum number of items to display at once.

    Returns:
      The index of the selected item.
    """

    start_index = 0
    end_index = min(start_index + max_visible, len(items))

    while True:
        print("\n")
        for i, item in enumerate(items[start_index:end_index],
                                 start=start_index):
            print(f"{i+1}. {item}")

        print(f"\n=== [Page {start_index // max_visible + 1}/" +
              f"{len(items) // max_visible + 1}] ===")

        choice = input("Enter the number of your choice," +
                       "'p' previous page, 'n' next page, or 'q' to quit: >")
        try:
            choice = int(choice)
            if 1 <= choice <= len(items):
                return choice - 1
        except ValueError:
            if choice.lower() == 'p':
                start_index = max(0, start_index - max_visible)
                end_index = min(start_index + max_visible, len(items))
            elif choice.lower() == 'n':
                start_index = min(len(items) - max_visible,
                                  start_index + max_visible)
                end_index = min(start_index + max_visible, len(items))
            elif choice.lower() == 'q':
                return None


if __name__ == '__main__':
    podcast_directory = "/home/edb/podparser/"
    file_list = read_files_in_directory(podcast_directory)
    # options = ["Option 1", "Option 2", "Option 3", "Option 4"]
    # options = file_list
    options = []
    for i in file_list:
        if ".mp3.txt" in i:
            options.append(i)

    selected_pod = curses.wrapper(select_from_list, options)

    title_url_tuples = []
    options = []

    mp3_file_list = read_episodes_from_file(selected_pod)

    for i in mp3_file_list:
        if ".mp3" in i:
            options.append(i)

    for i in options:
        j = i.split(' _|_ ')
        title_url_tuples.append((j[0], j[1]))

    title_url_dict = {}

    for i in title_url_tuples:
        title_url_dict[i[0]] = i[1]

    options = []
    for i in title_url_dict.keys():
        options.append(i)

    for title, url in title_url_dict.items():
        # print(f"title: {title}, URL: {url}")
        # print(title)
        options.append(str(title))

    items = options
    selected_index = scrollable_list(items)

    if selected_index is not None:
        episode_date_title = items[selected_index]
        print(f'episode_date_title="{episode_date_title}"')
        episode_url = title_url_dict[episode_date_title]
        print(f'episode_url="{episode_url}"')
        exit()

    print(f"TITLE={episode_date_title}")
    print(episode_url)
'''


    selected_item = scrollable_list(options, max_visible=17)
    print(f'selected item={selected_item}')

    # selected_mp3 = curses.wrapper(select_from_list, options)
    # print(f'selected mp3: {selected_mp3}')

    print(f'title: {selected_item}')
    print(f'  URL: {title_url_dict[selected_item]}')
'''
