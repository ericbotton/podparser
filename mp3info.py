import mutagen


def print_mp3_metadata(file_path):
    """Prints the metadata of an MP3 file.

    Args:
        file_path: The path to the MP3 file.
    """

    audio = mutagen.File(file_path)

    print("Metadata for:", file_path)
    for key, value in audio.items():
        print(f"{key}: {value}")
