from setuptools import setup, find_packages


setup(
    name='filewatcher',
    version='1.0',
    description='PO-411',
    url='https://github.com/goDeni/filewatcher',
    packages=find_packages('.'),
    install_requires=[
        'systemd', 'jinja2', 'pyinotify'
    ],
    entry_points={
        'console_scripts': [
            'fwr = filewatcher.cmd.cmd:main',
            'fwr-server = filewatcher.cmd.server:main',
            'fwr-sync = filewatcher.cmd.syncronizer:main'
        ]
    },
)
