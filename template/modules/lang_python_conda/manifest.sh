MODULE_NAME="lang_python_conda"
MODULE_DESCRIPTION="Python conda environment manager"
ACTIVATE_WHEN=("python_env_manager=conda")
DEPENDS_ON=("lang_python")
CONFLICTS_WITH=("lang_python_uv")
REQUIRED_VARS=("project_name" "project_description" "author_name")
