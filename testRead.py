from warcio.archiveiterator import ArchiveIterator
import json

with open("..\\sampleData\\attachments\\single\\test123\\data\\warc\\4.warc", "rb") as stream:
    for record in ArchiveIterator(stream):
        if record.rec_type == "metadata" and record.content_type == "application/json":
            metadata = json.load(record.content_stream())
            print(metadata["Date"])
            print(metadata["From"])
