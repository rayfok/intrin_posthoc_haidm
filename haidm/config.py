import os

APPLICATION_ROOT = '/'
DATABASE_FILENAME = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    'var', 'haidm.db'
)
