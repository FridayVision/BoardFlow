from setuptools import find_packages, setup

setup(
    name="dagster",
    packages=find_packages(exclude=["dagster_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
