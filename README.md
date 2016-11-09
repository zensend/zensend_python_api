[![Build Status](https://travis-ci.org/zensend/zensend_python_api.svg?branch=master)](https://travis-ci.org/zensend/zensend_python_api)

# ZenSend Python bindings 

## Installation

You don't need this source code unless you want to modify the
package. If you just want to use the ZenSend Python bindings, you
should run:

    pip install --upgrade zensend

or

    easy_install --upgrade zensend

See http://www.pip-installer.org/en/latest/index.html for instructions
on installing pip. If you are on a system with easy_install but not
pip, you can use easy_install instead. If you're not using virtualenv,
you may have to prefix those commands with `sudo`. You can learn more
about virtualenv at http://www.virtualenv.org/

To install from source, run:

    python setup.py install

## Documentation

Please see https://zensend.io/public/docs for the most up-to-date documentation.

## Testing

We commit to being compatible with Python 2.6+, Python 3.3+ and PyPy.  We need to test against all of these environments to ensure compatibility. For local testing, we use [tox](http://tox.readthedocs.org/) to handle testing across environments.

## Manual Testing

    import zensend
    client = zensend.Client("Yw4jIcm9qhofQfxFs2iaxQ", "http://localhost:8084")
    response = client.lookup_operator("441234567890")

## Uploading to pypi

    python setup.py sdist upload

