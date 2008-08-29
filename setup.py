from setuptools import setup, find_packages

setup(
    name='Dijkstar',
    version='1.0',
    description='Dijkstra/A* path finding functions',
    long_description="""
Dijkstar
++++++++

Dijkstar is an implementation of Dijkstra's single-source shortest-paths
algorithm. If a destination node is given, the algorithm halts when that node
is reached; otherwise it continues until paths from the source node to all
other nodes are found.

Accepts an optional cost (or "weight") function that will be called on every
iteration.

Also accepts an optional heuristic function that is used to push the algorithm
toward a destination instead of fanning out in every direction. Using such a
heuristic function converts Dijkstra to A* (and this is where the name
"Dijkstar" comes from).

Performance is decent on a graph with 100,000+ nodes. Runs in around .5
seconds on average .

See the source for the required graph structure:

https://guest:guest@svn.byCycle.org/spinoffs/Dijkstar

Latest development version:

https://guest:guest@svn.byCycle.org/spinoffs/Dijkstar#egg=Dijkstar-dev

    """,
    license='BSD/MIT',
    author='Wyatt L Baldwin, byCycle.org',
    author_email='wyatt@byCycle.org',
    keywords='Dijkstra A* algorithms',
    url='http://wyattbaldwin.com/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        ],
    packages=find_packages(),
    zip_safe=False,
    install_requires=(),
    test_suite = 'nose.collector',
)

