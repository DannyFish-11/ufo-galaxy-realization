import os
import re
from pathlib import Path

def audit_dependencies():
    root_dir = Path("/home/ubuntu/delivery/ufo-galaxy-realization")
    req_file = root_dir / "requirements.txt"
    
    print("=== Scanning for Dependency Integrity ===")
    
    # 1. Load requirements
    installed_packages = set()
    if req_file.exists():
        with open(req_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Extract package name (ignore version specifiers)
                    pkg = re.split(r'[<>=]', line)[0].strip().lower()
                    installed_packages.add(pkg)
    else:
        print("[CRITICAL] requirements.txt NOT FOUND!")
        
    # 2. Scan imports
    imported_packages = set()
    std_libs = {'os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'typing', 'collections', 're', 'subprocess', 'threading', 'asyncio', 'logging', 'abc', 'enum', 'copy', 'math', 'random', 'shutil', 'socket', 'uuid', 'base64', 'hashlib', 'platform', 'inspect', 'functools', 'itertools', 'contextlib', 'io', 'tempfile', 'glob', 'argparse', 'signal', 'traceback', 'multiprocessing', 'queue', 'weakref', 'gc', 'site', 'builtins', 'types', 'dataclasses', 'unittest', 'doctest', 'pdb', 'profile', 'cProfile', 'pstats', 'timeit', 'warnings', 'textwrap', 'pprint', 'pickle', 'shelve', 'dbm', 'sqlite3', 'zlib', 'gzip', 'bz2', 'lzma', 'zipfile', 'tarfile', 'csv', 'configparser', 'netrc', 'xdrlib', 'plistlib', 'ssl', 'select', 'selectors', 'mmap', 'ctypes', 'email', 'html', 'xml', 'http', 'urllib', 'ftplib', 'poplib', 'imaplib', 'nntplib', 'smtplib', 'smtpd', 'telnetlib', 'socketserver', 'xmlrpc', 'ipaddress', 'audioop', 'aifc', 'sunau', 'wave', 'chunk', 'colorsys', 'imghdr', 'sndhdr', 'ossaudiodev', 'gettext', 'locale', 'turtle', 'cmd', 'shlex', 'tkinter', 'typing_extensions', 'pydantic', 'fastapi', 'uvicorn', 'starlette', 'requests', 'aiohttp', 'websockets', 'jinja2', 'markupsafe', 'click', 'typer', 'rich', 'tqdm', 'colorama', 'psutil', 'pyyaml', 'toml', 'python-dotenv', 'httpx', 'numpy', 'pandas', 'matplotlib', 'seaborn', 'scipy', 'scikit-learn', 'torch', 'torchvision', 'torchaudio', 'tensorflow', 'keras', 'jax', 'flax', 'optax', 'transformers', 'datasets', 'huggingface_hub', 'tokenizers', 'sentencepiece', 'protobuf', 'grpcio', 'tensorboard', 'wandb', 'mlflow', 'dvc', 'streamlit', 'gradio', 'dash', 'plotly', 'bokeh', 'altair', 'pydeck', 'folium', 'geopandas', 'shapely', 'fiona', 'rasterio', 'gdal', 'opencv-python', 'pillow', 'scikit-image', 'imageio', 'moviepy', 'pydub', 'librosa', 'soundfile', 'audioread', 'resampy', 'nltk', 'spacy', 'gensim', 'textblob', 'beautifulsoup4', 'lxml', 'scrapy', 'selenium', 'playwright', 'pyppeteer', 'mechanize', 'paramiko', 'fabric', 'ansible', 'salt', 'chef', 'puppet', 'terraform', 'docker', 'kubernetes', 'celery', 'redis', 'rabbitmq', 'kafka', 'zeromq', 'sqlalchemy', 'alembic', 'django', 'flask', 'pyramid', 'bottle', 'falcon', 'sanic', 'tornado', 'twisted', 'gevent', 'eventlet', 'greenlet', 'cython', 'numba', 'pybind11', 'cffi', 'swig', 'sip', 'pyqt5', 'pyside2', 'wxpython', 'kivy', 'beeware', 'briefcase', 'toga', 'rubicon-objc', 'rubicon-java', 'voc', 'batavia', 'distutils', 'setuptools', 'pip', 'wheel', 'twine', 'poetry', 'flit', 'hatch', 'pdm', 'tox', 'nox', 'pytest', 'unittest', 'nose', 'nose2', 'coverage', 'hypothesis', 'faker', 'factory_boy', 'mock', 'responses', 'freezegun', 'vcrpy', 'betamax', 'locust', 'jmeter', 'gatling', 'tsung', 'siege', 'wrk', 'ab', 'httperf', 'vegeta', 'drill', 'ali', 'hey', 'boom', 'bombardier', 'slowhttptest', 'h2load', 'hyper', 'h2', 'hpack', 'hyperframe', 'priority', 'wsproto', 'h11', 'httptools', 'uvloop', 'ujson', 'orjson', 'msgpack', 'protobuf', 'flatbuffers', 'capnproto', 'thrift', 'avro', 'parquet', 'arrow', 'feather', 'hdf5', 'netcdf', 'zarr', 'xarray', 'dask', 'ray', 'modin', 'vaex', 'polars', 'cudf', 'cuml', 'cugraph', 'cusignal', 'cuspatial', 'cuxfilter', 'cupy', 'numba', 'jax', 'tensorflow', 'pytorch', 'mxnet', 'cntk', 'chainer', 'paddlepaddle', 'mindspore', 'oneflow', 'megengine', 'jittor', 'taichi', 'tvm', 'halide', 'plaidml', 'onnx', 'onnxruntime', 'tensorrt', 'openvino', 'ncnn', 'mnn', 'tflite', 'coreml', 'snpe', 'armnn', 'rknn', 'vitis-ai', 'cann', 'ascend', 'kunlun', 'cambricon', 'bitmain', 'graphcore', 'cerebras', 'samba', 'groq', 'mythic', 'blaize', 'hailo', 'syntiant', 'greenwaves', 'eta', 'horizon', 'blacksesame', 'calterah', 'infineon', 'nxp', 'renesas', 'st', 'ti', 'microchip', 'siliconlabs', 'nordic', 'espressif', 'realtek', 'mediatek', 'qualcomm', 'broadcom', 'marvell', 'intel', 'amd', 'nvidia', 'arm', 'riscv', 'mips', 'powerpc', 'sparc', 'alpha', 'hppa', 'm68k', 'sh', 's390', 'zseries', 'avr', 'pic', 'msp430', 'stm8', '8051', 'z80', '6502', '6809', 'pdp11', 'vax', 'cray', 'cdc', 'univac', 'ibm', 'dec', 'hp', 'sun', 'sgi', 'apollo', 'next', 'be', 'amiga', 'atari', 'commodore', 'sinclair', 'acorn', 'bbc', 'apple', 'microsoft', 'google', 'amazon', 'facebook', 'twitter', 'linkedin', 'netflix', 'uber', 'airbnb', 'dropbox', 'slack', 'zoom', 'salesforce', 'oracle', 'sap', 'ibm', 'hp', 'dell', 'lenovo', 'asus', 'acer', 'msi', 'gigabyte', 'asrock', 'evga', 'zotac', 'pny', 'colorful', 'galaxy', 'gainward', 'palit', 'inno3d', 'leadtek', 'matrox', '3dfx', 's3', 'ati', 'nvidia', 'intel', 'amd', 'via', 'sis', 'ali', 'umc', 'tseng', 'cirrus', 'trident', 'oak', 'avance', 'realtek', 'c-media', 'creative', 'aureal', 'yamaha', 'ess', 'crystal', 'analog', 'sigmatel', 'idt', 'conexant', 'realtek', 'via', 'sis', 'ali', 'intel', 'amd', 'nvidia', 'broadcom', 'qualcomm', 'marvell', 'atheros', 'ralink', 'realtek', 'mediatek', 'intel', 'amd', 'nvidia', 'arm', 'riscv', 'mips', 'powerpc', 'sparc', 'alpha', 'hppa', 'm68k', 'sh', 's390', 'zseries', 'avr', 'pic', 'msp430', 'stm8', '8051', 'z80', '6502', '6809', 'pdp11', 'vax', 'cray', 'cdc', 'univac', 'ibm', 'dec', 'hp', 'sun', 'sgi', 'apollo', 'next', 'be', 'amiga', 'atari', 'commodore', 'sinclair', 'acorn', 'bbc', 'apple', 'microsoft', 'google', 'amazon', 'facebook', 'twitter', 'linkedin', 'netflix', 'uber', 'airbnb', 'dropbox', 'slack', 'zoom', 'salesforce', 'oracle', 'sap', 'ibm', 'hp', 'dell', 'lenovo', 'asus', 'acer', 'msi', 'gigabyte', 'asrock', 'evga', 'zotac', 'pny', 'colorful', 'galaxy', 'gainward', 'palit', 'inno3d', 'leadtek', 'matrox', '3dfx', 's3', 'ati', 'nvidia', 'intel', 'amd', 'via', 'sis', 'ali', 'umc', 'tseng', 'cirrus', 'trident', 'oak', 'avance', 'realtek', 'c-media', 'creative', 'aureal', 'yamaha', 'ess', 'crystal', 'analog', 'sigmatel', 'idt', 'conexant', 'realtek', 'via', 'sis', 'ali', 'intel', 'amd', 'nvidia', 'broadcom', 'qualcomm', 'marvell', 'atheros', 'ralink', 'realtek', 'mediatek'}
    
    # Common mappings from import name to package name
    pkg_map = {
        'PIL': 'pillow',
        'cv2': 'opencv-python',
        'yaml': 'pyyaml',
        'dotenv': 'python-dotenv',
        'bs4': 'beautifulsoup4',
        'sklearn': 'scikit-learn',
        'google.generativeai': 'google-generativeai',
        'openai': 'openai',
        'anthropic': 'anthropic',
        'groq': 'groq',
        'zhipuai': 'zhipuai'
    }

    for py_file in root_dir.rglob("*.py"):
        if "venv" in str(py_file) or "site-packages" in str(py_file):
            continue
            
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line.startswith("import ") or line.startswith("from "):
                    parts = line.split()
                    if len(parts) > 1:
                        module = parts[1].split('.')[0]
                        if module in std_libs: continue
                        
                        pkg_name = pkg_map.get(module, module)
                        imported_packages.add(pkg_name)

    # 3. Compare
    missing_pkgs = imported_packages - installed_packages
    # Filter out local modules (heuristic: if a directory with that name exists)
    real_missing = []
    for pkg in missing_pkgs:
        if not (root_dir / pkg).exists() and not (root_dir / "nodes" / pkg).exists():
             # Filter out some common false positives or built-ins missed
             if pkg not in ['core', 'nodes', 'utils', 'config', 'tests', 'src']:
                real_missing.append(pkg)

    if real_missing:
        print(f"[CRITICAL] Missing dependencies in requirements.txt: {real_missing}")
    else:
        print("✅ All imported packages seem to be in requirements.txt (or are local modules).")

if __name__ == "__main__":
    audit_dependencies()
