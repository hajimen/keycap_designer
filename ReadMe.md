# keycap-designer

**keycap-designer** is a Python-based open-source application to design keycap printing images.
[DecentKeyboards](https://www.etsy.com/shop/DecentKeyboards) accepts the artifacts
as complete printing-ready data.

keycap-designer is good for designing a keycap set. A keycap set should have a consistent design across its keycaps.
keycap-designer helps a lot to make a consistent design.

So the learning curve may be too steep if you need just one or two keycaps. In that case, please send me the
printing image file, without struggling keycap-designer.

keycap-designer requires some knowledge of Python. It makes an artifact from a Python script that you write.
Look at `content/tutorial_1.py` to `content/tutorial_3.py` and `content/tutorial_junana.py`.

keycap-designer assumes that all keycaps are white. No colored keycaps. (But you can make alike ones with
Junana profile keycaps.)

## Requirements

- Windows PC or Mac

  - You can manage to do with other OSes. A PDF viewer is required.

- Python 3.11, 3.12, or 3.13

  - Windows: Download from [python.org](https://www.python.org/downloads/)

  - Mac: I recommend [Homebrew](https://brew.sh/)

- [Visual Studio Code (VSCode)](https://code.visualstudio.com/) and its
[Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

- [Adobe Acrobat Reader](https://get.adobe.com/reader/)

## Supported profiles and sizes

keycap-designer supports **XDA** and **Junana** profiles.

### XDA

The name "XDA" is not very precise. In this app, "XDA" is 9.5 mm height. Some shops say 9.3 or 9.2 mm.
They are identical.

keycap-designer supports:

- 1u
- 1.25u
- 1.5u
- 1.75u
- 2u
- 2.25u
- 2.75u

And can do front-side printing with 1u.

### Junana

**Junana** is a brand new profile from DecentKeyboards.
MX stem variation keycap is **Junana MX**. No other variations yet.

- Designed for 17 mm key pitch, but can do with 19 mm
- Junana MX is compatible with MX, Kailh Choc v2, and Gateron Low Profile switches
- Both convex and concave are available for all sizes
- Can print seamlessly on the all sides

The size variations are:

- 1u
- 1.5u
- 2.25u

**CAUTION**: The unit of Junana is 17 mm. The 2.25u is almost equivalent to 2u of 19 mm pitch.

More details: [DecentKeyboards](https://www.etsy.com/shop/DecentKeyboards)

## How to start

1. Install Python and VSCode.
2. In VSCode, install Python extension.
3. Make a working folder of keycap-designer. You will manage the folder with git.
4. Open the folder with VSCode.
5. Shift+Ctrl+P, choose "Python: Create Environment...", create a new venv or something, and activate it.
6. Open a new terminal and run `pip install keycap-designer`.
7. Run `keycap-designer` in the terminal. Initialize the folder. You will find `content`, `font`, `layout`, and `.vscode` directories are made.
8. Exit the app.
9. Open `content/tutorial_1.py` in VSCode and look at it.

## Content script: At a glance

### XDA profile

```python
from keycap_designer.manuscript import *


def generate():
    TEST_IMAGE = here() / 'test_image.png'
    # here() returns a pathlib.Path object representing the folder which contains the caller's source file.
    # In other words, 'test_image.png' should be in the same folder with this file.

    m_mandatory = Profile('XDA') @ Specifier('1u')
    # Profile and Specifier objects are mandatory Descriptor objects.
    # By combining Descriptor objects with @ operator, a Manuscript object is made.

    # About Specifier:
    # 1.5 unit (Tab key) is '15u', no period between 1 and 5.
    # Bump key is 'Homing 1u'.

    m_image = m_mandatory @ TopImage(TEST_IMAGE)
    # TopImage() returns a Descriptor object which represents a printing image and the printing side.
    # You can combine a Manuscript object with a Descriptor object by @ operator and make a Manuscript object.

    red = sRGBColor('#FF0000')
    green = sRGBColor('#00FF00')
    blue = sRGBColor('#0000FF')

    s_center_red = Style(
        size=4.5,
        # font size. The unit is mm.

        x_loc=0.,
        y_loc=0.,
        # [xy]_loc are the distance from the origin. The origin is specified by [hv]_o and align.
        # The unit is mm.

        font=APP_FONT_DIR / 'OpenSans-VariableFont_wdth,wght.ttf',
        # APP_FONT_DIR is ./font folder.
        # You can use OS_FONT_DIR too.
        # You can use variable fonts. The 'OpenSans-VariableFont_wdth,wght.ttf' is also a variable font.

        h_o=Center,
        align=Center,
        v_o=Center,
        # Layout to center of the printable area.
        # h denotes 'horizontal', v denotes 'vertical', and o denotes 'origin'.

        color=red,
        # Legend's color.

        side=TopSide
    )
    # Style object is required for Legend object.

    s_left_blue = s_center_red.mod(h_o=Left, align=Left, v_o=Top, color=blue)
    # You can modify Style object by mod().
    # Descriptor / Manuscript objects are immutable. Use returned objects.

    s_front_green = s_center_red.mod(side=FrontSide, color=green)
    # Look at 'side=FrontSide'. Front-side printing is available on 1u.

    legend = Legend({s_center_red: 'Red', s_left_blue: 'Blue', s_front_green: 'Green'})
    # You can combine multiple legends, of course.

    m_legend = m_mandatory @ legend
    # Legends on white background.

    m_image_legend = m_image @ legend
    # Legends on image.

    return [m_image, m_legend, m_image_legend]  # The app requires Manuscript object list.


CONTENT = generate()  # CONTENT will be imported from the app.
```

The script above generates the preview image below:

<img width="478" height="274" alt="Generated preview" src="https://raw.githubusercontent.com/hajimen/keycap_designer/refs/heads/readme-img/xda-preview.jpg" />

Gray area around top and front-side area is margin area. The area will be trimmed while printing.
The margin area also indicates the edge tolerance of printing.
In the script and the preview above, nothing is placed on the margin area.
The image and legends are cropped.

Look at the colors of legends. They look much paler than red: <img width="20px" height="20px" src="https://raw.githubusercontent.com/hajimen/keycap_designer/refs/heads/readme-img/red.png" />,
green: <img width="20px" height="20px" src="https://raw.githubusercontent.com/hajimen/keycap_designer/refs/heads/readme-img/green.png" />, and blue: <img width="20px" height="20px" src="https://raw.githubusercontent.com/hajimen/keycap_designer/refs/heads/readme-img/blue.png" />.
This represents the limit of printable colors. The saturation limit of printable colors are much paler than screen colors.
The saturation of those colors are truncated to printable colors. The preview image simulates printed colors.
Yes, keycap-designer implements ICC color management.

If you need the most saturated printable colors, use `DeviceRGBColor` with `Relative` instead of `sRGBColor` like shown in `tutorial_2.py`.
For images, use `Relative`, `RelativeNoBpc`, or `Saturation` like shown in `tutorial_3.py`.
The default is `Perceptual`.

Printed keycaps are:

<img width="491" height="500" alt="Printed keycaps" src="https://raw.githubusercontent.com/hajimen/keycap_designer/refs/heads/readme-img/xda-printed.jpg" />

# Junana profile

```python
from keycap_designer.manuscript import *


def generate():
    '''
    DecentKeyboard custom printing can do much for Junana.
    Let's see the difference.
    Unlike XDA, I can print all five sides of keycaps.
    '''
    ms: list[Manuscript] = []
    m = Profile('Junana') @ Specifier('1u')

    style = Style(2, 1, 1., APP_FONT_DIR / 'OpenSans-VariableFont_wdth,wght.ttf')
    front = style.mod(x_loc=1.5, y_loc=1.5, side=FrontSide)

    pale_red = sRGBColor('#FFB4B4')
    pale_blue = sRGBColor('#B4B4FF')

    ms.append(m @ Legend({style: 'BC'}) @ BackgroundColor(pale_red))
    # BackgroundColor object affects all five sides.

    ms.append(m @ Legend({style: 'Top SC'}) @ SideColor({TopSide: pale_red}))
    # If you just fill top-side, use SideColor object.

    ms.append(m @ Legend({front: 'Front SC'}) @ SideColor({FrontSide: pale_blue}))
    # SideColor object of front-side becomes like this.

    ms.append(m @ Legend({style: 'Top SC', front: 'BC'}) @ SideColor({TopSide: pale_blue}) @ BackgroundColor(pale_red))
    # You can combine BackgroundColor and SideColor objects.

    # You can see front-side legends are a bit deformed. It is adjusted to look good
    # when it is printed to actual keycaps (deformation correction).
    # Good but not perfect, sorry.

    ms.append(m @ Wallpaper(here() / 'test_pattern.png'))
    # Wallpaper covers all five sides.
    # No deformation correction in this case.

    ms.append(m @ Wallpaper(here() / 'test_image.png'))
    # You can print one image file on all five sides seamlessly.
    # No deformation correction.

    return ms


CONTENT = generate()
```

The script above generates the preview image below:

<img width="747" height="180" alt="Generated preview" src="https://raw.githubusercontent.com/hajimen/keycap_designer/refs/heads/readme-img/junana-preview.jpg" />

In this case, you can see that image is placed on margin area. They will be printed actually.

Look at "Front SC" area. There is margin area at the bottom of "Front SC" area, and nothing is placed on there.
How does it become?

Look at "Front SC" legend. It is deformed and shortened in the vertical direction. This is deformation correction.
It becomes square when it is printed.

Printed keycaps are:

<img width="319" height="500" alt="Printed keycaps" src="https://raw.githubusercontent.com/hajimen/keycap_designer/refs/heads/readme-img/junana-printed.jpg" />

The margin area at the bottom of "Front SC" area remains unprinted.

Look at the lattice pattern keycap. The left side is quite deformed.
You should be careful of the deformation if you need all-sided printing.

## How to order custom keycaps

Send me, [DecentKeyboards](https://www.etsy.com/shop/DecentKeyboards), the preview PDF file.
It contains complete printing-ready data as an attachment file.

## License

MIT License.

## Development

### Keycap profile

You can inject your `keycap_designer.profile.Profile` object to `keycap_designer.profile.PROFILES`.
Mimic `keycap_designer.profile.xda`.

Do you need deform correction like Junana profile? It is quite hard. Good luck.

### Version

`keycap_designer/_version.py` will be generated by `python -m build --wheel`.

### Unit test

`pip install pdf2image`.

Download [poppler-windows](https://github.com/oschwartz10612/poppler-windows) latest binary release,
extract `poppler-*` to `./tests` folder, and rename the `poppler-*` to `poppler`.
