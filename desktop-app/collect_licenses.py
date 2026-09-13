"""Copy installed package license notices into the distributable vendor folder."""
from importlib.metadata import distributions
from pathlib import Path
import re
import shutil
import sys

target = Path(__file__).resolve().parent / 'vendor'
target.mkdir(exist_ok=True)
shutil.copy2(Path(sys.base_prefix) / 'LICENSE.txt', target / 'PYTHON-LICENSE.txt')
for dist in distributions():
    name = re.sub(r'[^A-Za-z0-9_.-]', '_', dist.metadata['Name'])
    for file in dist.files or []:
        if file.name.lower().startswith(('license', 'copying', 'copyright')):
            source = Path(dist.locate_file(file))
            if source.is_file():
                folder = target / 'licenses' / name
                folder.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, folder / file.name)
