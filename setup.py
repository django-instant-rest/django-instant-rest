from setuptools import setup, find_packages

setup(name='django_instant_rest',
    version='0.1',
    description='',
    python_requires='>=3',
    url='https://github.com/django-instant-rest/django-instant-rest.git',
    author='',
    author_email='',
    license='MIT',
    zip_safe=False,
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        'setuptools',
        'argon2-cffi>=20.1',
        'pyjwt>=2',
    ],
)
