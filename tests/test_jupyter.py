import unittest
from tests.common import OUTPUT_DIR
from keycap_designer._jupyter import _generate_pdf, _unit_test_setting, show_inline
from keycap_designer.manuscript import *
from tests.common import assert_pdf


def get_content():
    TEST_IMAGE = here() / 'resource/land.png'
    m_mandatory = Profile('XDA') @ Specifier('1u')
    m_image = m_mandatory @ TopImage(TEST_IMAGE)
    red = sRGBColor('#FF0000')
    green = sRGBColor('#00FF00')
    blue = sRGBColor('#0000FF')

    s_center_red = Style(
        size=4.5,
        x_loc=0.,
        y_loc=0.,
        font=APP_FONT_DIR / 'OpenSans-VariableFont_wdth,wght.ttf',
        h_o=Center,
        align=Center,
        v_o=Center,
        color=red,
        side=TopSide
    )
    s_left_blue = s_center_red.mod(h_o=Left, align=Left, v_o=Top, color=blue)
    s_front_green = s_center_red.mod(side=FrontSide, color=green)
    legend = Legend({s_center_red: 'Red', s_left_blue: 'Blue', s_front_green: 'Green'})
    m_legend = m_mandatory @ legend
    m_image_legend = m_image @ legend
    return [m_image, m_legend, m_image_legend]


class TestJupyter(unittest.TestCase):
    def test_generate_pdf(self):
        _unit_test_setting(OUTPUT_DIR)
        pdf_name = _generate_pdf(get_content(), 'test_generate_pdf.pdf')
        assert_pdf(self, pdf_name, 'test_generate_pdf')

    def test_show_inline(self):
        html = show_inline(get_content(), 96.)._repr_html_()

        import hashlib
        digest = hashlib.md5(html.encode()).hexdigest()
        with open(OUTPUT_DIR / (digest + '.html'), 'w') as f:
            f.write('''<!doctype html>
<html lang=en>
<head>
<meta charset=utf-8>
<title>blah</title>
</head>
<body>''')
            f.write(html)
            f.write('</body></html>')
        self.assertEqual(digest, 'da31ac1e96d52422e293ef2f60d51c19', f'Wrong digest: {digest}')
