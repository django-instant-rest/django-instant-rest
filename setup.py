from setuptools import setup

setup(name='django_instant_rest',
    version='0.1',
    description='',
    python_requires='>=3',
    url='https://github.com/django-instant-rest/django-instant-rest.git',
    author='',
    author_email='',
    license='MIT',
    zip_safe=False,
    packages=['django_instant_rest'],
    install_requires=[
        'setuptools',
        'argon2-cffi>=20.1',
        'pyjwt>=2',
    ],
)
