def _install():
    import piplite
    import asyncio
    asyncio.run(piplite.install('cmm-16bit'))
    asyncio.run(piplite.install('keycap_designer'))


_install()
