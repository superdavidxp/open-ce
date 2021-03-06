"""
*****************************************************************
Licensed Materials - Property of IBM
(C) Copyright IBM Corp. 2020. All Rights Reserved.
US Government Users Restricted Rights - Use, duplication or
disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
*****************************************************************
"""
import os
import pathlib

import utils

utils.check_if_conda_build_exists()

# pylint: disable=wrong-import-position
import conda_build.api
from conda_build.config import get_or_merge_config
import conda_build.metadata
# pylint: enable=wrong-import-position

def render_yaml(path, variants=None, variant_config_files=None, schema=None, permit_undefined_jinja=False):
    """
    Call conda-build's render tool to get a list of dictionaries of the
    rendered YAML file for each variant that will be built.
    """
    config = get_or_merge_config(None, variant=variants)
    config.variant_config_files = variant_config_files
    config.verbose = False

    if not os.path.isfile(path):
        metas = conda_build.api.render(path,
                                       config=config,
                                       bypass_env_check=True,
                                       finalize=False)
    else:
        # api.render will only work if path is pointing to a meta.yaml file.
        # For other files, use the MetaData class directly.
        # The absolute path is needed because MetaData seems to do some caching based on file name.
        metas = conda_build.metadata.MetaData(
                            os.path.abspath(path),
                            config=config).get_rendered_recipe_text(permit_undefined_jinja=permit_undefined_jinja)
    if schema:
        utils.validate_dict_schema(metas, schema)
    return metas

def get_output_file_paths(meta, variants):
    """
    Get the paths of all of the generated packages for a recipe.
    """
    config = get_or_merge_config(None, variant=variants)
    config.verbose = False

    out_files = conda_build.api.get_output_file_paths(meta, config=config)

    # Only return the package name and the parent directory. This will show where within the output
    # directory the package should be.
    result = []
    for out_file in out_files:
        path = pathlib.PurePath(out_file)
        result.append(os.path.join(path.parent.name, path.name))

    return result
