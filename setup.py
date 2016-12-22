from setuptools import setup

setup(
    name='tty_radio',
    packages=['tty_radio'],
    version='0.1.5',
    description="Terminal player for online radio streams.",
    author='Ryan Farley',
    author_email='rfarley3@gmu.edu',
    url='https://github.com/rfarley3/radio',
    download_url='https://github.com/rfarley3/radio/tarball/0.1.5',
    keywords=['radio', 'somafm', 'streaming', 'mpg123'],
    classifiers=[],
    install_requires=[
        'beautifulsoup4',
        'pyfiglet',
    ],
    entry_points={
        'console_scripts': [
            'radio = tty_radio.__main__:main',
        ]
    },
)
