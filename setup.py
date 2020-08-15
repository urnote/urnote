from setuptools import setup, find_packages

setup(
    name='urnote',

    version='0.3',

    description='A program that utilizes spaced repetition to review your notes written in Markdown',
    long_description='',

    url='https://github.com/urnote/urnote',

    author='Jeffrey',
    author_email='Jeffrey.S.Teo@gmail.com',

    license='GPL-3.0',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',

        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Operating System :: OS Independent',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    platforms='any',

    keywords=['markdown', 'notebook', 'note', 'spaced repetition'],

    packages=find_packages(exclude=['test*']),

    install_requires=['sqlalchemy', 'colorama'],

    python_requires='~=3.3',

    entry_points={
        'console_scripts': ['note=note.__main__:run'],
    },

    package_data={
        'note': [
            '*/locales/*',
            '*/locales/zh_CN/LC_MESSAGES/*',
        ],
    }
)
