from distutils.core import setup


with open('README') as fp:
    long_description = fp.read()


setup(
    name='Dijkstar',
    version='2.3.0',
    description='Dijkstra/A*',
    long_description=long_description,
    license='MIT',
    author='Wyatt Baldwin',
    author_email='self@wyattbaldwin.com',
    keywords='Dijkstra A* algorithms',
    url='https://github.com/wylee/Dijkstar',
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
    ],
    packages=['dijkstar']
)
