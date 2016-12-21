from setuptools import setup

setup(
    name='radio',
    version='0.0.1',
    description="Terminal player for online radio streams.",
    author='rfarley3',
    author_email='rfarley3@gmu.edu',
    packages=['radio'],
    install_requires=[
        'beautifulsoup4',
        'pyfiglet',
    ],
    entry_points={
        'console_scripts': [
            'radio = radio.__main__:main',
        ]
    },
)
