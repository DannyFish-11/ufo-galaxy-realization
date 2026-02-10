import os
import re
import sys

def get_imports(file_path):
    imports = set()
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                parts = line.split()
                if len(parts) > 1:
                    module = parts[1].split('.')[0]
                    imports.add(module)
    return imports

def get_requirements(req_path):
    reqs = set()
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    reqs.add(line.split('==')[0].split('>=')[0].lower())
    return reqs

project_root = "/home/ubuntu/delivery/ufo-galaxy-realization"
all_imports = set()
builtin_modules = sys.builtin_module_names

for root, dirs, files in os.walk(project_root):
    for file in files:
        if file.endswith('.py'):
            all_imports.update(get_imports(os.path.join(root, file)))

reqs = get_requirements(os.path.join(project_root, "requirements.txt"))
std_libs = {'os', 'sys', 'json', 'time', 'logging', 'asyncio', 'subprocess', 'pathlib', 'typing', 'dataclasses', 'enum', 'datetime', 'threading', 'signal', 'abc', 'collections', 'functools', 'inspect', 'math', 'random', 're', 'shutil', 'socket', 'sqlite3', 'struct', 'traceback', 'uuid', 'weakref', 'platform', 'queue', 'io', 'base64', 'hashlib', 'tempfile', 'glob', 'argparse', 'ast', 'contextlib', 'copy', 'csv', 'ctypes', 'decimal', 'difflib', 'email', 'errno', 'fnmatch', 'gc', 'getpass', 'gzip', 'heapq', 'hmac', 'html', 'http', 'importlib', 'itertools', 'locale', 'mimetypes', 'multiprocessing', 'netrc', 'numbers', 'operator', 'optparse', 'pickle', 'pkgutil', 'pprint', 'pydoc', 'runpy', 'sched', 'secrets', 'selectors', 'shelve', 'shlex', 'site', 'smtplib', 'sndhdr', 'socketserver', 'ssl', 'stat', 'string', 'stringprep', 'sysconfig', 'tabnanny', 'tarfile', 'telnetlib', 'textwrap', 'timeit', 'token', 'tokenize', 'trace', 'tracemalloc', 'tty', 'types', 'unicodedata', 'unittest', 'urllib', 'uu', 'warnings', 'wave', 'weakref', 'webbrowser', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile', 'zipimport', 'zlib'}

missing = []
for imp in all_imports:
    imp_lower = imp.lower()
    if imp_lower not in reqs and imp_lower not in std_libs and imp not in builtin_modules:
        # 排除项目内部模块
        if not os.path.exists(os.path.join(project_root, imp)) and not os.path.exists(os.path.join(project_root, imp + ".py")):
             missing.append(imp)

print("Potential missing dependencies:", missing)
