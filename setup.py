from setuptools import find_packages, setup


from dijkstar import __version__


with open('README.rst') as fp:
    long_description = fp.read()


setup(
    name='Dijkstar',
    version=__version__,
    description='Dijkstra/A*',
    long_description=long_description,
    license='MIT',
    author='Wyatt Baldwin',
    author_email='self@wyattbaldwin.com',
    keywords='Dijkstra A* algorithms',
    url='https://github.com/wylee/Dijkstar',
    packages=find_packages(),
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
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
