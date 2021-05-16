from setup import ExtensionInstaller


def loader():
    return WeatherlFlowTempestAPIInstaller()


class WeatherlFlowTempestAPIInstaller(ExtensionInstaller):
    def __init__(self):
        super(WeatherlFlowTempestAPIInstaller, self).__init__(
            version="0.1",
            name='weatherflowtempestapi',
            description='Driver for Weatherflow tempest stations that uses their websocket API.',
            author="",
            author_email="",
            files=[('bin/user', ['bin/user/weatherflowtempestapi.py'])]
        )
