MODULE_NAME="lang_python_uv"
MODULE_DESCRIPTION="Python uv package manager"
ACTIVATE_WHEN=("python_env_manager=uv")
DEPENDS_ON=("lang_python")
CONFLICTS_WITH=("lang_python_conda")
REQUIRED_VARS=("project_name" "project_description" "author_name")
