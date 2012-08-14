from setuptools import setup, find_packages
import os
from telapi import VERSION

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name                = "telapi",
    version             = VERSION,
    description         = "TelAPI REST API client and InboundXML generator",
    author              = "TelAPI",
    author_email        = "help@telapi.com",
    url                 = "https://github.com/telapi/telapi-python/",
    keywords            = ["telapi", "inboundxml", "telephony", "rest"],
    install_requires    = ["requests"],
    packages            = find_packages(),
    classifiers         = [
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Telephony"
    ],
    long_description    = read('README.md'),
)
