from setuptools import setup

setup(
    name='tty_radio',
    packages=['tty_radio'],
    version='1.1.2',
    description=(
        "Linux/OS X RESTful player for online radio streams, " +
        "like SomaFM and WCPE. Comes with a terminal UI " +
        "flavored with colors and ASCII art " +
        "and web UI for remote management."),
    author='Ryan Farley',
    author_email='rfarley3@gmu.edu',
    url='https://github.com/rfarley3/radio',
    download_url='https://github.com/rfarley3/radio/tarball/1.1.2',
    keywords=['radio', 'somafm', 'streaming', 'mpg123'],
    classifiers=[],
    install_requires=[
        'beautifulsoup4',
        'pyfiglet',
        'bottle',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'radio = tty_radio.__main__:main_ui',
            'radio_server = tty_radio.__main__:main_serv',
        ]
    },
    include_package_data=True,
)
