from distutils.core import setup, find_packages

LICENSE_PATH = 'LICENSE'
README_PATH = 'readme.md'


def load_text(path):
    with open(path) as fh:
        text = fh.read()

    return text

setup(
    name='Twim'
    , version='1.0.0'
    , description='Terminal based Twitter client'
    , author='Shinsaku Yamamura'
    , author_email='randozou@gmail.com'
    , url='https://github.com/gretchi/twim'
    , license=load_text(LICENSE_PATH)
    , long_description=load_text(README_PATH)
    , packages=[
        'requests_oauthlib'
        , 'requests'
        , 'emoji'
    ]
)
