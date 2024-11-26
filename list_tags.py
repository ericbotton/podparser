#!/usr/bin/env python
import sys
from mutagen.id3 import ID3
import downloadepisode

if len(sys.argv) > 1:
    mp3_file = sys.argv[1]

tag_list, tag_dict = downloadepisode.get_mp3_tags(mp3_file)
for tag in tag_list:
    #short_tag = tag[:73]
    short_tag = tag
    print(f"{short_tag}")
#downloadepisode.print_mp3_tags(tag_dict)
