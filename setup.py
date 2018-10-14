from setuptools import setup, find_packages


setup(
    name='filewatcher',
    version='1.0',
    description='PO-411',
    packages=find_packages('.'),
    install_requires=[
        'systemd', 'jinja2'
    ],
    entry_points={
        'console_scripts': [
            'fwr = filewatcher.cmd.cmd:main',
            'fwr-server = filewatcher.cmd.server:main',
        ]
    },
)
