# Setup for the checklist application
# Licensed under the MIT licences, 2019

import io

from setuptools import find_packages, setup

with io.open('README.md', "rt", encoding="utf8") as f:
    readme = f.read()

setup(
    name="checklist_app",
    version="0.0.1",
    url="https://bebleo.github.io/checklist",
    license="MIT",
    maintainer="Bebleo",
    maintainer_email="",
    description="An app to create, store, and track checklists.",
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask", "flask-mail", "flask-wtf"],
    extras_require={"test": ["pytest", "coverage"]},
)