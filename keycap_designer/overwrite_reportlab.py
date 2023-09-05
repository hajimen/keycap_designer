from reportlab.pdfbase.pdfdoc import _mode2CS
from reportlab.pdfbase.pdfdoc import *


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


def loadImageFromSRC(self: PDFImageXObject, im):
    "Extracts the stream, width and height"
    fp = im.jpeg_fh()
    if fp:
        raise Exception('JPEG compressed image is not supported')
    else:
        self.width, self.height = im.getSize()
        raw = im.getRGBData()
        # assert len(raw) == self.width*self.height, "Wrong amount of data for image expected %sx%s=%s got %s" % (self.width,self.height,self.width*self.height,len(raw))
        self.streamContent = zlib.compress(raw)
        if rl_config.useA85:  # type: ignore
            self.streamContent = asciiBase85Encode(self.streamContent)
            self._filters = 'ASCII85Decode', 'FlateDecode'  # 'A85','Fl'
        else:
            self._filters = 'FlateDecode',  # 'Fl'

        icc_profile_body = im._image.info.get('icc_profile')
        if icc_profile_body is None:
            self.colorSpace = _mode2CS[im.mode]
        else:
            n_ch = {'L': 1, 'RGB': 3, 'CMYK': 4}.get(im.mode)
            if n_ch is not None:
                self.colorSpace = IccBasedColorspace(n_ch, icc_profile_body)  # type: ignore

        self.bitsPerComponent = 8
        self._checkTransparency(im)


def format(self: PDFImageXObject, document):
    S = PDFStream(content=self.streamContent)
    dict = S.dictionary
    dict["Type"] = PDFName("XObject")
    dict["Subtype"] = PDFName("Image")
    dict["Width"] = self.width
    dict["Height"] = self.height
    dict["BitsPerComponent"] = self.bitsPerComponent
    if type(self.colorSpace) == IccBasedColorspace:
        dict["ColorSpace"] = self.colorSpace.to_obj()  # type: ignore
    else:
        dict["ColorSpace"] = PDFName(self.colorSpace)
        if self.colorSpace == 'DeviceCMYK' and getattr(self, '_dotrans', None):
            dict["Decode"] = PDFArray([1, 0, 1, 0, 1, 0, 1, 0])
        elif getattr(self, '_decode', None):
            dict["Decode"] = PDFArray(self._decode)  # type: ignore
    dict["Filter"] = PDFArray(map(PDFName, self._filters))
    dict["Length"] = len(self.streamContent)
    if self.mask:
        dict["Mask"] = PDFArray(self.mask)
    if getattr(self, 'smask', None):
        dict["SMask"] = self.smask  # type: ignore
    return S.format(document)


def overwrite_reportlab():
    PDFImageXObject.loadImageFromSRC = loadImageFromSRC
    PDFImageXObject.format = format
