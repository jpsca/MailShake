#!/usr/bin/env python
"""
This file generates all the necessary files for packaging for the project.
Read more about it at https://github.com/jpscaletti/mastermold/
"""
data = {
    "title": "MailShake",
    "name": "mailshake",
    "pypi_name": "mailshake",
    "version": "1.191122",
    "author": "Juan-Pablo Scaletti",
    "author_email": "juanpablo@jpscaletti.com",
    "description": "Simplify sending email from your python app.",
    "copyright": "2013",
    "repo_name": "jpscaletti/mailshake",
    "home_url": "",
    "project_urls": {},
    "development_status": "5 - Production/Stable",
    "minimal_python": 3.6,
    "install_requires": [
        "html2text",
    ],
    "testing_requires": [
        "pytest",
        "pytest-cov",
    ],
    "development_requires": [
        "flake8",
        "ipdb",
        "tox",
    ],
    "entry_points": "",
    "coverage_omit": [],
}


def do_the_thing():
    import hecto

    hecto.copy(
        # "gh:jpscaletti/mastermold.git",
        "../mastermold",  # Path to the local copy of Master Mold
        ".",
        data=data,
        force=False,
        exclude=[
            ".*",
            ".*/*",
            "README.md",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
        ],
    )


if __name__ == "__main__":
    do_the_thing()
