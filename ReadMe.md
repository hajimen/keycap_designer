# keycap-designer

**keycap-designer** is a Python-based open-source application to design keycap printing images.
[DecentKeyboards](https://www.etsy.com/shop/DecentKeyboards) accepts the artifacts
as complete printing-ready data.

keycap-designer is good for designing keycap sets. A keycap set should have a consistent design across its keycaps.
keycap-designer helps a lot to make a consistent design.
So the learning curve may be too steep if you need just one or two keycaps. In that case, please send me the
printing image file.

keycap-designer requires some knowledge of Python. It makes the artifact from a Python script that you write.
Look at `content/tutorial_1.py`.

## Requirements

- Windows PC or Mac

You can manage to do with other OS, but it will be harder than you are guessing now, I guess.

- [Visual Studio Code (VSCode)](https://code.visualstudio.com/) and its
[Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

- [Adobe Acrobat Reader](https://get.adobe.com/jp/reader/)

## How to start

1. Download the latest ZIP file for your machine from [https://github.com/hajimen/keycap-designer/releases]
and extract to somewhere you like.
2. Launch `edit.bat` or `edit.sh`. It should open VSCode.
3. Launch `app.bat` or `app.sh` in the VSCode terminal.
4. From VSCode explorer, open `tutorial_1.py`.
5. In the app, run `load tutorial_1.py`. It should show a preview.
6. Compare the preview with `tutorial_1.py`.
7. Modify somewhere of the script, close the preview, and in the app, hit Enter key.

## Content script: At a glance

```python
from keycap_designer.manuscript import *


def generate():
    TEST_IMAGE = here() / 'test_image.png'
    # here() returns a pathlib.Path object representing the directory which contains the caller's source file.
    # In other words, 'test_image.png' should be in the same directory with this file.

    m_mandatory = Profile('XDA') @ Specifier('1u')
    # Profile and Specifier objects are the mandatory Descriptor objects.
    # By combining Descriptor objects with @ operator, a Manuscript object is made.

    # About Specifier:
    # 1.5 unit (Tab key) is '15u', no period between 1 and 5.
    # Bump key is 'Homing 1u'.

    m_image = m_mandatory @ TopImage(TEST_IMAGE)
    # TopImage() returns a Descriptor object which represents a printing image and the printing side.
    # You can combine a Manuscript object with a Descriptor object by @ operator and make a Manuscript object.

    return [m_image]


CONTENT = generate()  # CONTENT will be imported from the app.
```

## How to order custom keycaps

Send me, [DecentKeyboards](https://www.etsy.com/shop/DecentKeyboards), the preview PDF file.
It contains complete printing-ready data as an attachment file.

## License

MIT License.

## Development

### Dependencies

`cmm` module in the dependencies requires a special attention. It is not on PyPI.
See [https://github.com/hajimen/cmm]. Run `pip install cmm-*.whl` first if you prepare
venv by yourself.

### Keycap profile

You can inject your `keycap_designer.profile.Profile` object to `keycap_designer.profile.PROFILES`.
Mimic `keycap_designer.profile.xda`.

Do you need deform correction like Junana profile? It is quite hard. Good luck.

### Packaging

Prepare venv by yourself.
Run `pip install pyinstaller`, and from repository root directory,
Windows: `packaging/win.bat`, macOS: `sh packaging/osx.sh`.
The artifact should found in `./dist` directory.

### Version

`keycap_designer/_version.py` will be generated by `python -m build --wheel`.

### Unit test

`pip install pdf2image`.

Download [poppler-windows](https://github.com/oschwartz10612/poppler-windows) latest binary release,
extract `poppler-*` to `./tests` directory, and rename the `poppler-*` to `poppler`.