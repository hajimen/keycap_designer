import zlib
from reportlab.pdfbase.pdfdoc import _mode2CS  # type: ignore
from reportlab.pdfbase.pdfdoc import PDFStream, PDFName, PDFArray, PDFImageXObject
from reportlab.lib.rl_accel import asciiBase85Encode
from reportlab import rl_config
from reportlab.lib.utils import ImageReader
from reportlab.platypus.paragraph import Paragraph


class IccBasedColorspace:
    def __init__(self, n_ch, profile_body):
        self.n_ch = n_ch
        self.profile_body = profile_body

    def to_obj(self):
        from base64 import a85encode
        pdf_stream = PDFStream(content=a85encode(self.profile_body).decode('latin-1') + '~>')
        d = pdf_stream.dictionary
        d['N'] = self.n_ch
        d["Filter"] = PDFName('ASCII85Decode')
        d['Alternate'] = PDFName({1: 'DeviceGray', 3: 'DeviceRGB', 4: 'DeviceCMYK'}[self.n_ch])
        return PDFArray([PDFName('ICCBased'), pdf_stream])


def loadImageFromSRC(self: PDFImageXObject, im: ImageReader):
    "Extracts the stream, width and height"
    fp = im.jpeg_fh()
    if fp:
        raise Exception('JPEG compressed image is not supported')
    else:
        self.width, self.height = im.getSize()
        raw: bytes = im.getRGBData()
        # assert len(raw) == self.width*self.height, "Wrong amount of data for image expected %sx%s=%s got %s" % (self.width,self.height,self.width*self.height,len(raw))
        self.streamContent = zlib.compress(raw)  # type: ignore
        if rl_config.useA85:
            self.streamContent = asciiBase85Encode(self.streamContent)
            self._filters = 'ASCII85Decode', 'FlateDecode'  # 'A85','Fl'  # type: ignore
        else:
            self._filters = 'FlateDecode',  # 'Fl'  # type: ignore

        icc_profile_body = im._image.info.get('icc_profile')  # type: ignore
        if icc_profile_body is None:
            self.colorSpace = _mode2CS[im.mode]
        else:
            n_ch = {'L': 1, 'RGB': 3, 'CMYK': 4}.get(im.mode)
            if n_ch is not None:
                self.colorSpace = IccBasedColorspace(n_ch, icc_profile_body)  # type: ignore

        self.bitsPerComponent = 8
        self._checkTransparency(im)  # type: ignore


def format(self: PDFImageXObject, document):
    S = PDFStream(content=self.streamContent)
    dict = S.dictionary
    dict["Type"] = PDFName("XObject")
    dict["Subtype"] = PDFName("Image")
    dict["Width"] = self.width
    dict["Height"] = self.height
    dict["BitsPerComponent"] = self.bitsPerComponent
    if type(self.colorSpace) is IccBasedColorspace:
        dict["ColorSpace"] = self.colorSpace.to_obj()  # type: ignore
    else:
        dict["ColorSpace"] = PDFName(self.colorSpace)
        if self.colorSpace == 'DeviceCMYK' and getattr(self, '_dotrans', None):
            dict["Decode"] = PDFArray([1, 0, 1, 0, 1, 0, 1, 0])
        elif getattr(self, '_decode', None):
            dict["Decode"] = PDFArray(self._decode)  # type: ignore
    dict["Filter"] = PDFArray(map(PDFName, self._filters))  # type: ignore
    dict["Length"] = len(self.streamContent)
    if self.mask:
        dict["Mask"] = PDFArray(self.mask)
    if getattr(self, 'smask', None):
        dict["SMask"] = self.smask  # type: ignore
    return S.format(document)


def wrap(self, availWidth, availHeight):
    # Bug workaround for macOS

    # if availWidth<_FUZZ:
    #     #we cannot fit here
    #     return 0, 0x7fffffff
    # work out widths array for breaking
    self.width = availWidth
    style = self.style
    leftIndent = style.leftIndent
    first_line_width = availWidth - (leftIndent+style.firstLineIndent) - style.rightIndent
    later_widths = availWidth - leftIndent - style.rightIndent
    self._wrapWidths = [first_line_width, later_widths]
    if style.wordWrap == 'CJK':
        #use Asian text wrap algorithm to break characters
        blPara = self.breakLinesCJK(self._wrapWidths)
    else:
        blPara = self.breakLines(self._wrapWidths)
    self.blPara = blPara
    autoLeading = getattr(self,'autoLeading',getattr(style,'autoLeading',''))
    leading = style.leading
    if blPara.kind==1:
        if autoLeading not in ('','off'):
            height = 0
            if autoLeading=='max':
                for l in blPara.lines:
                    height += max(l.ascent-l.descent,leading)
            elif autoLeading=='min':
                for l in blPara.lines:
                    height += l.ascent - l.descent
            else:
                raise ValueError('invalid autoLeading value %r' % autoLeading)
        else:
            height = len(blPara.lines) * leading
    else:
        if autoLeading=='max':
            leading = max(leading,blPara.ascent-blPara.descent)
        elif autoLeading=='min':
            leading = blPara.ascent-blPara.descent
        height = len(blPara.lines) * leading
    self.height = height
    return self.width, height


def overwrite_reportlab():
    PDFImageXObject.loadImageFromSRC = loadImageFromSRC
    PDFImageXObject.format = format
    Paragraph.wrap = wrap
