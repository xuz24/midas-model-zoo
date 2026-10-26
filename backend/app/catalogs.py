from .records import catalog_entries


def get_datasets():
    return catalog_entries('datasets')


def get_papers():
    return catalog_entries('papers')


def get_software():
    return catalog_entries('software')
