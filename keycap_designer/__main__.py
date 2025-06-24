import faulthandler
faulthandler.enable()
import typing as ty
import os
import subprocess
from pathlib import Path
import importlib
import traceback
import sys
import platform

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter, PathCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import yes_no_dialog

from keycap_designer.constants import CURRENT_DIR, RESOURCE_DIR
from keycap_designer.manuscript import manuscript_to_artwork
from keycap_designer.preview import print_rc_map, print_preview


CONTENT_DIR_NAME = 'content'
FONT_DIR_NAME = 'font'
LAYOUT_DIR_NAME = 'layout'
VSCODE_DIR_NAME = '.vscode'
CONTENT_DIR = CURRENT_DIR / CONTENT_DIR_NAME
OUTPUT_DIR = CURRENT_DIR / 'tmp'
REPO_DIR_NAMES = [CONTENT_DIR_NAME, FONT_DIR_NAME, LAYOUT_DIR_NAME]
REPO_DIRS = [CURRENT_DIR / d for d in REPO_DIR_NAMES]
MODULE = None
IMPORTED_MODULE_D: dict[str, ty.Any] = {}


style = Style.from_dict({
    'module_name': '#00dd00',
    'pound': 'ansicyan',
    'sheet_size': '#884444',
    'separator': '#0000aa',
    'status': '#aa0000',
})
session = PromptSession(history=FileHistory('history.txt'), style=style)


def show_pdf(pdf: Path):
    s = platform.system()
    if s == 'Darwin':
        import shlex
        subprocess.Popen([f'open {shlex.quote(str(pdf))}'], shell=True)
    elif s == 'Windows':
        subprocess.Popen([str(pdf)], shell=True)
    else:
        print(f'Platform {s} is not supported. Open {str(pdf)} by yourself.')


def show_preview():
    if MODULE is None:
        raise Exception('show_preview called but MODULE is None.')
    if not hasattr(MODULE, 'CONTENT'):
        print(f"Error: {MODULE.__name__} doesn't have CONTENT.")
        return

    pdf = OUTPUT_DIR / f'{MODULE.__name__}_preview.pdf'
    try:
        print_preview([manuscript_to_artwork(i) for i in MODULE.CONTENT], pdf)
    except PermissionError:
        print('Error: Close the PDF file.')
        return
    except FileNotFoundError as e:
        print(f'File not found: {str(e)}')
        return
    except Exception as e:
        print('Error: show_preview failed. Exception:')
        traceback.print_exception(e)
        return
    show_pdf(pdf)


def rc_map(text: str):
    layout_fn = text.split()[1]
    p = Path(CURRENT_DIR / LAYOUT_DIR_NAME / layout_fn)
    pdf = OUTPUT_DIR / f'{p.stem}_rc_map.pdf'
    try:
        print_rc_map(p, pdf)
    except PermissionError:
        print('Error: Close the PDF file.')
        return
    except Exception as e:
        print('Error: rc_map failed. Exception:')
        traceback.print_exception(e)
        return
    show_pdf(pdf)


def reload():
    global MODULE
    if MODULE is None:
        print('Error: content not loaded yet.')
        return
    try:
        MODULE = importlib.reload(MODULE)
        IMPORTED_MODULE_D[MODULE.__name__] = MODULE
    except Exception as e:
        print(f'Error: {MODULE.__name__} reload failed. Exception:')
        traceback.print_exception(e)
        MODULE = None
        return
    if not hasattr(MODULE, 'CONTENT'):
        print(f"Error: {MODULE.__name__} doesn't have CONTENT.")
        MODULE = None
        return
    show_preview()


def load(text: str):
    global MODULE
    fn = text.split()[1]
    p = Path(CONTENT_DIR / fn).relative_to(CONTENT_DIR)
    module_name = str.join('.', (CONTENT_DIR_NAME, ) + p.parts[:-1] + (p.stem, ))
    importlib.invalidate_caches()
    try:
        if module_name in IMPORTED_MODULE_D:
            MODULE = importlib.reload(IMPORTED_MODULE_D[module_name])
        else:
            MODULE = importlib.import_module(module_name)
    except Exception as e:
        MODULE = None
        print(f'Error: {module_name} import failed. Exception:')
        traceback.print_exception(e)
        return
    IMPORTED_MODULE_D[module_name] = MODULE
    if not hasattr(MODULE, 'CONTENT'):
        print(f"Error: {module_name} doesn't have CONTENT.")
        MODULE = None
        return
    show_preview()
    return


def remove_file_if_exists(p: Path):
    if not p.exists():
        return True
    try:
        p.unlink()
    except Exception:
        return False
    return True


def pump():
    module_path_completer = PathCompleter(get_paths=lambda: [CONTENT_DIR_NAME], file_filter=lambda fn: os.path.isdir(fn) or fn.endswith('.py'))
    layout_path_completer = PathCompleter(get_paths=lambda: [LAYOUT_DIR_NAME], file_filter=lambda fn: os.path.isdir(fn) or fn.endswith('.json'))
    root_completer = NestedCompleter.from_nested_dict({
        'show': None,
        'reload': None,
        'load': module_path_completer,
        'rc_map': layout_path_completer,
        'help': None,
        'exit': None
    })

    message = []

    message += [
        ('class:module_name', '('),
        ('class:module_name', 'None' if MODULE is None else MODULE.__name__),
        ('class:module_name', ')'),
    ]

    message.append(('class:pound', '# '))

    text: str = session.prompt(message, completer=root_completer, bottom_toolbar='To exit this app, type "exit" and hit Enter key.')

    if text == 'show':
        show_preview()
    if text.startswith('rc_map'):
        rc_map(text)
    elif text == '' or text == 'reload':
        reload()
    elif text.startswith('load'):
        load(text)
    elif text.startswith('exit'):
        return False
    elif text.startswith('help'):
        print('''Commands:
load {content script file}:
    Loads the content script and shows the preview.
reload (or just hit Enter key):
    Reloads current content script and shows the preview.
show:
    Shows the preview of current content script without reloading.
rc_map {layout KLE JSON file}:
    Shows Row/Col map of the layout KLE JSON file.
exit:
    Exits this app.''')
    else:
        print(f'Error: {text} is invalid.')

    return True


def repo_ok():
    if not OUTPUT_DIR.is_dir():
        if not remove_file_if_exists(OUTPUT_DIR):
            print(f'Error: Cannot remove {OUTPUT_DIR} file. Please remove the file by yourself.')
            sys.exit(1)
        OUTPUT_DIR.mkdir()

    if all(d.is_dir() for d in REPO_DIRS + [CURRENT_DIR / VSCODE_DIR_NAME]):
        return True

    result = yes_no_dialog(
        title="keycap-designer",
        text="Do you initialize current directory for keycap-designer?"
    ).run()

    if result:
        import shutil
        for n, d in zip(REPO_DIR_NAMES, REPO_DIRS):
            shutil.copytree(RESOURCE_DIR / 'repo' / n, d, dirs_exist_ok=True)
        shutil.copytree(RESOURCE_DIR / 'repo/vscode', CURRENT_DIR / VSCODE_DIR_NAME, dirs_exist_ok=True)

    return result


def main():
    from keycap_designer import version
    print(f'keycap-designer {version} (C) 2023-2025 DecentKeyboards; MIT License')
    if not repo_ok():
        return
    if len(sys.argv) > 1:
        v = sys.argv[1]
        try:
            vp = Path(v)
        except Exception:
            print('Error: The arg {v} is not a valid file path.')
            sys.exit(1)
        try:
            rp = vp.relative_to(CONTENT_DIR)
        except Exception:
            print('Error: The file {v} is not in ./content folder.')
            sys.exit(1)
        load('load ' + str(rp))
        
    sys.path.append(os.getcwd())
    print('Type "help" and hit Enter key to show the command help.')
    while True:
        cont = pump()
        if not cont:
            break


if __name__ == '__main__':
    main()
