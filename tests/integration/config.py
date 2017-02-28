import os

BASE_DIR = os.path.dirname(__file__)

VIR_ROOT_DIR = os.path.join(BASE_DIR, 'vir_env')
VIR_DB_PATH = VIR_ROOT_DIR + '/.NOTE/note.db3'

ExpectedDbPath = (BASE_DIR + r'\res\{}\{}\.NOTE\note.db3').format
ExpectedRootDir = (BASE_DIR + r'\res\{}\{}').format
