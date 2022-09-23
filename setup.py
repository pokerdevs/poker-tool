from setuptools import setup, find_namespace_packages

setup(
    name="poker-tool",
    author='Pokerdevs',
    author_email='pokerdevs@proton.me',
    use_scm_version={
        'write_to': 'pokerdevs/poker_tool/_version.py',
        'write_to_template': '__version__ = "{version}"',
    },
    setup_requires=['setuptools_scm>6.0,<7'],
    install_requires=[],
    extras_require={
        'test': ['pytest']
    },
    description="Collection of useful CLI tools for poker players",
    packages=find_namespace_packages(include=['pokerdevs.*', 'tests.*', 'scripts.*']),
    package_data={
    },
    entry_points={
        'console_scripts': [
            'poker_tool=scripts.pokerdevs.poker_tool.poker_tool:main',
        ]
    },
)