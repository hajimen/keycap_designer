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
