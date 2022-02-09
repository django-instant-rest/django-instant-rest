
# How to Contribute

Firstly, welcome! Thanks for being interested in the project.

- If you're looking to report a bug or request a specific feature, search for it in [Issues](https://github.com/django-instant-rest/django-instant-rest/issues), and create a new issue if necessary.
- If you're looking to get involved, and don't have a particular feature in mind, try posting in [Discussions](https://github.com/django-instant-rest/django-instant-rest/discussions).

# Local Development Tools

All commands listed on this page are intended to work with the following toolset:

```bash
python3 --version
# Python 3.8.2

pip --version
# pip 22.0.3 from /Users/me/Library/Python/3.8/lib/python/site-packages/pip (python 3.8)
```

# How to Run Tests Locally

```bash
cd tests
pip install -r requirements.txt
python3 manage.py test --verbosity=2
```