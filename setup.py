from distutils.core import setup


setup(
    name='Dijkstar',
    version='1.0',
    description='Dijkstra/A* path finding functions',
    long_description="""
Dijkstar
++++++++

Dijkstar is an implementation of Dijkstra's single-source shortest-paths
algorithm. If a destination node is given, the algorithm halts when that
node is reached; otherwise it continues until paths from the source node
to all other nodes are found.

Accepts an optional cost (or "weight") function that will be called on
every iteration.

Also accepts an optional heuristic function that is used to push the
algorithm toward a destination instead of fanning out in every
direction. Using such a heuristic function converts Dijkstra to A* (and
this is where the name "Dijkstar" comes from).

Performance is decent on a graph with 100,000+ nodes. Runs in around .5
seconds on average .

See the source for the required graph structure:

https://bitbucket.org/wyatt/dijkstar/src/tip/dijkstar/__init__.py

""",
    license='BSD/MIT',
    author='Wyatt Lee Baldwin',
    author_email='wyatt.lee.baldwin@gmail.com',
    keywords='Dijkstra A* algorithms',
    url='https://bitbucket.org/wyatt/dijkstar',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
    ],
)
