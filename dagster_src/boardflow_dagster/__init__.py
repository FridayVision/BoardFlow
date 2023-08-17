from dagster import (
    Definitions,
    load_assets_from_modules,
    load_assets_from_package_module,
)
from .assets import bgg_data

bgg_data_assets = load_assets_from_package_module(package_module=bgg_data)


defs = Definitions(
    assets=bgg_data_assets,
)
