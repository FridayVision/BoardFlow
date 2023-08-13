from setuptools import find_packages, setup

setup(
    name="boardflow_dagster",
    packages=find_packages(exclude=["dagster_tests"]),
    install_requires=[
        "dagster",
        "dagster-dbt",
        "lxml",
        "ratelimit",
        "tenacity",
        "pandas",
        "dbt-core",
        "dbt-duckdb",
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
