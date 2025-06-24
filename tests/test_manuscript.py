import unittest
from keycap_designer.manuscript import *


FONT_PATH = Path(APP_FONT_DIR / 'OpenSans-VariableFont_wdth,wght.ttf')
OUTPUT_DIR = CURRENT_DIR / 'tmp'


class TestManuscript(unittest.TestCase):
    def test_matmul(self):
        self.assertEqual(Layout('US-ASCII') % Layout('ISO'), Layout('ISO'))
        m = Layout('US-ASCII') @ Col(1)
        self.assertIsInstance(m, Manuscript)
        self.assertEqual(m.col.v, 1)  # type: ignore
        m2 = Layout('US-ASCII') @ Col(2)
        self.assertNotEqual(m, m2)
        m3 = m2 @ Col(1)
        self.assertEqual(m, m3)
        g = Group('a') % Group('b')
        self.assertIsInstance(g, Group)
        self.assertEqual(g.v, 'a\nb')
        m = Group('a') @ Comment('b')
        self.assertIsInstance(m, Manuscript)
        self.assertEqual(Repeat(2) % Repeat(3), Repeat(6))

    def test_style(self):
        s = Style(3., 0., 0., FONT_PATH)
        self.assertEqual(s.mod(size=4., x_loc=1., y_loc=2.), Style(4., 1., 2., FONT_PATH))
        self.assertEqual(s.shift(x=1.), Style(3., 1., 0., FONT_PATH))
        self.assertEqual(sRGBColor(0, 0, 0), sRGBColor(0, 0, 0))

    def test_legend(self):
        s1 = Style(3., 0., 0., FONT_PATH)
        s2 = Style(3., 0., 5., FONT_PATH)
        self.assertEqual(Legend({s1: 'S1'}) % Legend({s2: 'S2'}), Legend({s1: 'S1', s2: 'S2'}))
        sp = Specifier('1u')
        self.assertEqual((Legend({s1: 'S1'}) @ sp) @ Legend({s2: 'S2'}), Legend({s1: 'S1', s2: 'S2'}) @ sp)

    def test_list(self):
        m = Row(1)
        s1 = Style(3., 0., 0., FONT_PATH)
        s2 = Style(3., 0., 5., FONT_PATH)
        ls = [Legend({s1: 'S1'}), Legend({s2: 'S2'})]
        ms = m >> ls
        self.assertEqual(ms[0], Row(1) @ Legend({s1: 'S1'}))

        cs = Col(0) ** ls
        self.assertEqual(cs[1], Col(1) @ Legend({s2: 'S2'}))

        rs = Row(0) ** ls
        self.assertEqual(rs[1], Row(1) @ Legend({s2: 'S2'}))

        gs = Group('g') >> ls
        self.assertEqual(gs[1], Group('g') @ Legend({s2: 'S2'}))

    def test_manuscript_to_artwork(self):
        RES = CURRENT_DIR / 'tests/resource'
        m = Row(1) @ Profile('XDA') @ Specifier('1u') @ BackgroundColor(sRGBColor(200, 200, 200))
        s = Style(1., 1.5, 1., FONT_PATH)
        s_lt = s
        s_cc = s.mod(h_o=Center, align=Center, v_o=Center, x_loc=0.)
        s_rb = s.mod(h_o=Right, align=Right, v_o=Bottom)
        ls = []
        for fn in ['land.png', 'port.png']:
            for fit in [Aspect, Crop, Expand, PixelWise]:
                ls.append(Legend({s_lt: fn, s_cc: fit.name}) @ TopImage(RES / fn, fit=fit))
        for ip in [Cubic, Nearest]:
            ls.append(Legend({s_rb: ip.name}) @ TopImage(RES / 'land.png', interpolate=ip))
        ls.append(Legend({s_lt: 'alpha'}) @ TopImage(RES / 'alpha.png', fit=Crop, interpolate=Cubic) @ BackgroundColor(sRGBColor(200, 0, 200)))
        ms = m >> ls
        aws = [manuscript_to_artwork(i) for i in ms]
        for i, aw in enumerate(aws):
            img = (aw.side_image[TopSide] // 257).astype(np.uint8)
            op = CURRENT_DIR / f'tests/oracle/test_manuscript_to_artwork_{i}.png'
            oracle = cv2.imread(str(op), cv2.IMREAD_UNCHANGED)
            if not np.all(img == oracle):
                import PIL.Image as PILImageModule
                from keycap_designer.color_management import ICC_DIR
                pi = PILImageModule.fromarray(cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA))
                WORKSPACE_PROFILE_FILENAME = 'Linear P3D65.icc'
                with open(ICC_DIR / WORKSPACE_PROFILE_FILENAME, 'rb') as f:
                    pi.info['icc_profile'] = f.read()
                rp = OUTPUT_DIR / f'test_result/test_manuscript_to_artwork_{i}.png'
                if not rp.parent.exists():
                    rp.parent.mkdir()
                pi.save(rp)
                self.fail(f'Oracle and result differ. Compare {CURRENT_DIR / f"tests/oracle/test_manuscript_to_artwork_{i}.png"} with {rp}')
            # import PIL.Image as PILImageModule
            # pi = PILImageModule.fromarray(cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA))
            # # pi.show()
            # from keycap_designer.color_management import ICC_DIR
            # WORKSPACE_PROFILE_FILENAME = 'Linear P3D65.icc'
            # with open(ICC_DIR / WORKSPACE_PROFILE_FILENAME, 'rb') as f:
            #     pi.info['icc_profile'] = f.read()
            # pi.save(op)
