import re

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from utils.misc import load_all_spider


class FileEventHandler(FileSystemEventHandler):
    def __init__(self, schedule):
        self.schedule = schedule
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        if event.is_directory:
            print("directory moved from {0} to {1}".format(event.src_path, event.dest_path))
        else:
            print("file moved from {0} to {1}".format(event.src_path, event.dest_path))

    def on_created(self, event):
        if event.is_directory:
            print("directory created:{0}".format(event.src_path))
        else:
            self.schedule.spiders = load_all_spider(self.schedule.settings["SPIDER_DIR"])
            print("file created:{0}".format(event.src_path))

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            self.schedule.spiders = load_all_spider(self.schedule.settings["SPIDER_DIR"])
            print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            self.schedule.spiders = load_all_spider(self.schedule.settings["SPIDER_DIR"])
            print("file modified:{0}".format(event.src_path))


def load_filter_spider(schedule):
    filter_spiders = schedule.settings["FILTER_SPIDER"]
    load_spiders = load_all_spider(schedule.settings["SPIDER_DIR"])
    assert load_spiders, "[define] expect match local spiders, given nothing"
    if not isinstance(load_spiders, list):
        raise TypeError('variable load_spiders expect list type, given %s' % type(load_spiders))
    for spider in filter_spiders:
        for load_spider in load_spiders:
            if re.search(spider, load_spider.__name__):
                schedule.spiders[load_spider.name] = load_spider


def start_observer(path, schedule):
    # load_filter_spider(schedule)
    observer = Observer()
    event_handler = FileEventHandler(schedule)
    observer.schedule(event_handler, path, True)
    observer.start()

    # observer.join()
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     observer.stop()
