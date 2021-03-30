from setuptools import find_packages, setup


with open('README.rst') as fp:
    long_description = fp.read()


# NOTE: These convolutions are to avoid importing from dijkstar because
#       dependencies might not be installed at this point.
version_file = 'dijkstar/__init__.py'
with open(version_file) as fp:
    for line in fp:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip("'")
            break
    else:
        raise RuntimeError('Could not find __version__ in %s' % version_file)


setup(
    name='Dijkstar',
    version=version,
    description='Dijkstra/A*',
    long_description=long_description,
    license='MIT',
    author='Wyatt Baldwin',
    author_email='self@wyattbaldwin.com',
    keywords='Dijkstra A* algorithms',
    url='https://github.com/wylee/Dijkstar',
    packages=find_packages(),
    install_requires=[
        'six',
    ],
    extras_require={
        'dev': [
            'coverage',
            'flake8',
            'tox',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
