import os
from setuptools import setup


this_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_dir, 'README.rst')) as f:
    LONG_DESCRIPTION = '\n' + f.read()

REQUIREMENTS = filter(
    None,
    open(os.path.join(this_dir, 'requirements.txt')).read().splitlines()
)

setup(
    name='harprofiler',
    version='0.1.0',
    description='Automated web page profiler',
    packages=['harprofiler', 'harprofiler.tests'],
    install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': [
            'harprofiler = harprofiler.harprofiler:main',
            'haruploader = harprofiler.haruploader:main',
        ]
    },
    author='edX Test Engineering Team',
    author_email='cgoldberg _at_ gmail.com',
    url='https://github.com/edx/harprofiler',
    long_description=LONG_DESCRIPTION,
    keywords='web profiler automation har harstorage'.split(),
    license='Apache2',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ]
)
