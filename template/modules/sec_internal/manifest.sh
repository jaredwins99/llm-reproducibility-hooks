MODULE_NAME="sec_internal"
MODULE_DESCRIPTION="Internal/proprietary data security posture"
ACTIVATE_WHEN=("data_sensitivity~=internal")
DEPENDS_ON=()
CONFLICTS_WITH=()
REQUIRED_VARS=("project_name")
