from distutils.core import setup


with open('README') as fp:
    long_description = fp.read()


setup(
    name='Dijkstar',
    version='2.1.dev0',
    description='Dijkstra/A*',
    long_description=long_description,
    license='MIT',
    author='Wyatt Lee Baldwin',
    author_email='wyatt.lee.baldwin@gmail.com',
    keywords='Dijkstra A* algorithms',
    url='https://bitbucket.org/wyatt/dijkstar',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
    packages=['dijkstar']
)
