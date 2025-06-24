from keycap_designer.manuscript import *


def generate():
    '''
    Let's see a bit elaborate pattern.

    - Using serial numbers for image files (see ./starter-kit folder)

    It is quite common pattern. Just use Python's feature.

    - Using keyboard layout

    You can use KLE (http://www.keyboard-layout-editor.com/) to make a preview with layout.
    From 'Raw data' tab, you can download/upload JSON file.
    CAUTION: Don't use copy-and-paste from/to the browser. Use 'Download JSON' or 'Upload JSON' button.

    Now we are going to see Row and Col objects.

    Row and Col objects corresponds to the front legends in KLE JSON file.
    Open ./layout/p2ppcb-starter-kit.json by http://www.keyboard-layout-editor.com/
    and look at the properties of the keys.

    Run the app, type 'rc_map p2ppcb-starter-kit.json', and hit Enter key.
    You will see RC map of the KLE JSON file.
    '''
    ms: list[Manuscript] = []
    # ms becomes the return value of this function.

    m = Profile('XDA') @ Specifier('1u') @ Layout('p2ppcb-starter-kit') @ Relative
    # We already have seen Profile and Specifier objects in tutorial_1.py.
    # Layout object corresponds to a KLE JSON file in ./layout folder.
    # Relative is required for DeviceRGBColor.

    for i in range(11):
        ms.append(m @ TopImage(here() / f'starter-kit/{i:0>2}.png', fit=Crop))
        # {i:0>2} is a fancy feature of Python.

    ms[:3] = Row(0) >> Col(0) ** ms[:3]
    # Please take a breath: new operator >> and **.
    # The line above is equivalent to:
    # ms[0] @= Row(0) @ Col(0)
    # ms[1] @= Row(0) @ Col(1)
    # ms[2] @= Row(0) @ Col(2)

    ms[3:6] = Row(1) >> Col(0) ** ms[3:6]
    ms[6:9] = Row(2) >> Col(0) ** ms[6:9]
    ms[9:11] = Row(3) >> Col(1) ** ms[9:11]  # Be careful: There is no (3, 0) key. See rc_map.

    rb = Style(
        3.,  # font size by mm
        1.,  # x_loc by mm
        1.,  # y_loc by mm
        APP_FONT_DIR / 'OpenSans-VariableFont_wdth,wght.ttf',  # font path
        h_o=Right, align=Right, v_o=Bottom,
        color=DeviceRGBColor('#00ff00')  # If you need the most saturated color, try DeviceRGBColor.
    )

    rb2 = rb.mod(y_loc=4.)
    # Just modifying an existing Style object. No need to specify everything.

    ms[0] @= Legend({rb: 'F2'})
    ms[1] @= Legend({rb: 'Home'})
    ms[2] @= Legend({rb2: 'Page', rb: 'Up'})
    ms[3] @= Legend({rb: 'Del'})
    ms[4] @= Legend({rb: 'End'})
    ms[5] @= Legend({rb2: 'Page', rb: 'Down'})
    ms[6] @= Legend({rb: 'Left'})
    ms[7] @= Legend({rb: 'Up'})
    ms[8] @= Legend({rb2: 'OSM', rb: 'Ctrl'})
    ms[9] @= Legend({rb: 'Down'})
    ms[10] @= Legend({rb: 'Right'})

    return ms


CONTENT = generate()
