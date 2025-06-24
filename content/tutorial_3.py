from keycap_designer.manuscript import *


def generate():
    '''
    Now let's see some low-profile but valuable features.
    '''
    ms: list[Manuscript] = []
    m = Profile('XDA') @ Specifier('1u') @ Layout('p2ppcb-starter-kit')
    for i in range(11):
        ms.append(m @ TopImage(here() / f'starter-kit/{i:0>2}.png', fit=Crop))
    # The lines above are the same with tutorial_2.py.

    ms.insert(9, m @ Skip(1))
    # Skip object is a filler for Row and Col operator **.
    # Skip object increments the Row/Col index and vanishes after ** operation.

    # Why do we need Skip object? Because a keyboard matrix can be sparse.
    # You can see the example of sparse matrix by 'rc_map ansi-104.json' in the app.
    # In the case, fill the blanks by Skip objects.
    # It makes easy to assign Row and Col objects, as shown below.

    ms = sum(
        [Row(i) >> Col(0) ** ms[i * 3: i * 3 + 3] for i in range(4)],
        []
    )
    # This is the example. Now len(ms) == 11 because the Skip object has vanished.

    if len(ms) != 11:
        raise Exception('Bad code.')

    pale_red = sRGBColor('#FFB4B4')
    pale_red_bc = BackgroundColor(pale_red)
    # You have already seen the legends have surrounding white outlines in the preview.
    # But not all the image is good for it. You can change the color by BackgroundColor object.
    # BackgroundColor object also affects margin area and all sides.
    # It is alike "keycap's color".

    rb = Style(
        3.,  # font size by mm
        1.,  # x_loc by mm
        1.,  # y_loc by mm
        APP_FONT_DIR / 'OpenSans-VariableFont_wdth,wght.ttf',  # font path
        h_o=Right, align=Right, v_o=Bottom)
    rb2 = rb.mod(y_loc=4.)
    front = rb.mod(side=FrontSide)

    ms[0] @= Legend({rb: 'Normal'})

    ms[1] @= Legend({rb: 'BC'})
    ms[1] @= pale_red_bc
    # Compare the legends of Normal key and BC key.

    ms[2] @= Legend({rb2: 'Aspect', rb: 'BC'})
    ms[2] @= TopImage(here() / 'starter-kit/02.png', fit=Aspect) @ pale_red_bc
    # First, ms[2] already contains Image object.
    # Descriptor object in Manuscript object can be overwritten.
    # In the case, right object overwrites left object.
    # Second, look at the color of image padding area.
    # fit=Aspect leaves image padding area as background.

    ms[3] @= Legend({rb2: 'Front', rb: 'BC'})
    ms[3] @= Legend({front: 'Front'}) @ pale_red_bc
    # ms[2] already contains Legend object. But in this case,
    # two Legend objects are combined into one, not overwritten.
    # Pay attention that BackgroundColor object affects top and front both.

    ms[4] @= Legend({rb2: 'Front', rb: 'SC'})
    ms[4] @= Legend({front: 'Front'}) @ SideColor({FrontSide: pale_red})
    # If you need to restrict the effect into one side, use SideColor object.
    # Please look at gray-ish margin areas too. SideColor object doesn't affect margin area's color.
    # BackgroundColor object does.

    ms[5] @= Legend({rb: 'Repeat'})
    ms[5] @= Repeat(3)
    # You can need multiple keycaps with the same design. Repeat object helps you.

    ms[6] @= Legend({
        rb.mod(variation_name='Condensed Regular'): 'Comment'
        # variation_name is for variable fonts.
    })
    ms[6] @= Comment('foo bar')
    # Comment object is a last resort.

    ms[7] @= Legend({
        rb.mod(size=2.): 'Wallpaper'
    })
    ms[7] @= TopImage(here() / 'starter-kit/07.png', fit=Aspect) @ Wallpaper(here() / 'test_pattern.png')
    # Wallpaper() returns BackgroundImage object which does image tiling.

    ms[8] @= Legend({rb: 'Rotation'})
    ms[8] @= Rotation(RotationAngle.CW)
    # In XDA 1u, it is a bit pointless :-)

    ms[9] @= Legend({rb: 'Relative'})
    ms[9] @= Relative
    # keycap_designer does color management. It is alike rocket science.
    # It is impossible to tell the meaning of "Relative" here.
    # The default is Perceptual. If you are not satisfied with the color tone,
    # try Relative, RelativeNoBpc, or Saturation.

    ms[10] @= Legend({rb.mod(size=1.5): 'Perceptual'})
    ms[10] @= TopImage(here() / 'starter-kit/09.png', fit=Crop)
    # To compare Relative (ms[9]) and Perceptual (default).

    m_supplement = Profile('XDA') @ Specifier('1u') @ Legend({rb: 'Sup'})
    # You can mix Layout and non-Layout Manuscript objects into one preview.

    return ms + [m_supplement]


CONTENT = generate()
