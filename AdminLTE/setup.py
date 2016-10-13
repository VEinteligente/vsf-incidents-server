from setuptools import setup

setup(
    name='django-adminlte',
    version='1.2',
    packages=['django_adminlte'],
    include_package_data=True,
    license='MIT License',
    description='AdminLTE Bootstrap Theme packaged for Django',
    long_description=open('README.md', 'r').read(),
    url='https://github.com/ricardotun/django-adminlte',
    author='Ricardo Tun',
    author_email='me@ricardotun.net',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities',
    ],
    keywords='django bootstrap admin theme',
    install_requires=[
        'django>=1.4',
    ],
)
