import os

BASE_DIR = os.path.dirname(__file__)

ExpectedDbPath = os.path.join(BASE_DIR, 'res', '{}', '{}', '.NOTE',
                              'note.db3').format
ExpectedRootDir = os.path.join(BASE_DIR, 'res', '{}', '{}').format
