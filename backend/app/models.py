from .records import catalog_entries


def get_models():
    return catalog_entries('models')
