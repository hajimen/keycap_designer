from frozendict import frozendict
from keycap_designer.profile import Aperture, CapBase
from keycap_designer.profile import Profile
from keycap_designer.constants import *


D = RESOURCE_DIR / 'area/xda'


def _ap(image_name: str):
    return Aperture(D / (image_name + '.png'))


cb1u = CapBase({
    TopSide: _ap('1u'),
    FrontSide: _ap('1u-front')
})

cb125u = CapBase({
    TopSide: _ap('125u'),
})

cb15u = CapBase({
    TopSide: _ap('15u'),
})

cb175u = CapBase({
    TopSide: _ap('175u'),
})

cb2u = CapBase({
    TopSide: _ap('2u'),
})

cb225u = CapBase({
    TopSide: _ap('225u'),
})

cb275u = CapBase({
    TopSide: _ap('275u'),
})


PROFILE = Profile(
    'XDA',
    frozendict({
        '1u': cb1u,
        'Homing 1u': cb1u,
        '125u': cb125u,
        '15u': cb15u,
        '175u': cb175u,
        '2u': cb2u,
        '225u': cb225u,
        '275u': cb275u,
    }),
    frozendict({
        'Homing 1u': 'homing',
    })
)
