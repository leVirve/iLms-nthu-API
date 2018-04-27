from setuptools import setup


def version():
    with open('ilms/__init__.py') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.replace("'", '').split()[-1]


setup(
    name='ilms-nthu',
    packages=['ilms'],
    install_requires=[
        'requests',
        'beautifulsoup4',
        'pyquery',
        'tqdm',
        'lxml',
        'click'
    ],
    entry_points={
        'console_scripts': ['ilms=ilms.cli:main'],
    },
    version=version(),
    description='iLms-NTHU API. An iLMS client for students, assistants and developers.',
    author='leVirve',
    author_email='gae.m.project@gmail.com',
    url='https://github.com/leVirve/iLms-nthu-API',
    license='MIT',
    platforms='any',
    keywords=['iLms', 'NTHU', 'API'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Customer Service',
        'Intended Audience :: System Administrators',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],)
