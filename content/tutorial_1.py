from keycap_designer.manuscript import *


def generate():
    '''
    Let's see the basic patterns of keycap_designer's content script.
    In many cases, you will not need to know more than what is in this file.

    To view the preview, run the app, input 'load tutorial_1', and hit Enter key.
    To reload and view, just hit Enter key.
    To exit from the app, 'exit'.

    Gray area around printing image is margin area. The area may be trimmed while printing.
    '''
    TEST_IMAGE_PATH = here() / 'test_image.png'
    # here() returns a pathlib.Path object representing the directory which contains the caller's source file.
    # In other words, 'test_image.png' should be in the same directory with this file.

    m_mandatory = Profile('XDA') @ Specifier('1u')
    # Profile and Specifier objects are the mandatory Descriptor objects.
    # By combining Descriptor objects with @ operator, a Manuscript object is made.

    # About Specifier:
    # 1.5 unit (Tab key) is '15u', no period between 1 and 5.
    # Bump key is 'Homing 1u'.

    m_image = m_mandatory @ TopImage(TEST_IMAGE_PATH)
    # TopImage() returns a Descriptor object which represents a printing image and the printing side.
    # You can combine a Manuscript object with a Descriptor object by @ operator and make a Manuscript object.

    m_image_crop = m_mandatory @ TopImage(TEST_IMAGE_PATH, fit=Crop)
    # m_image's printing result is portrait and leaves margin to the left and right.
    # By specifying fit=Crop, no margin. You can use Expand or PixelWise too.

    # About PixelWise:
    # PixelWise's resolution is 720 DPI. But it will not be printed pixelwise actually.
    # DecentKeyboards printing system does anti-bleed correction. It adjusts ink thickness
    # of edges to get high-fidelity result. So don't care about rescaling, and just use
    # the most convenient resolution.

    red = sRGBColor(255, 0, 0)  # Namely #FF0000.
    blue = sRGBColor(0, 0, 255)  # Namely #0000FF.

    s_center_red = Style(
        size=4.5,
        # font size. The unit is mm.

        x_loc=0.,
        y_loc=0.,
        # [xy]_loc are the distance from the origin. The origin is specified by [hv]_o and align.
        # The unit is mm.

        font=APP_FONT_DIR / 'damase_v.2.ttf',
        # APP_FONT_DIR is ./font directory.
        # You can use OS_FONT_DIR too.

        h_o=Center,
        align=Center,
        v_o=Center,
        # Layout to center of the printable area.

        color=red,
        # Legend's color.

        side=TopSide
    )
    # Style object is required for Legend object.

    s_left_blue = s_center_red.mod(h_o=Left, align=Left, v_o=Top, color=blue)
    # You can modify Style object by mod().
    # Descriptor / Manuscript objects are immutable. Use returned objects.

    s_left_blue = s_left_blue.shift(x=1., y=1.)
    # Shift() adds [xy] to [xy]_loc.
    # Again: Descriptor / Manuscript objects are immutable. Use returned objects.

    m_center_red = m_mandatory @ Legend({s_center_red: 'Red'})
    # Legend()'s arg is a dictionary. Why? The reason is the below.

    m_center_red_left_blue = m_mandatory @ Legend({s_center_red: 'Red', s_left_blue: 'Blue'})
    # Two styles of legends are here!

    m_image_legend = m_image @ Legend({s_center_red: 'Red'})
    # Legend over image is of course available.

    return [m_mandatory, m_image, m_image_crop, m_center_red, m_center_red_left_blue, m_image_legend]


CONTENT = generate()  # CONTENT will be imported from the app.
