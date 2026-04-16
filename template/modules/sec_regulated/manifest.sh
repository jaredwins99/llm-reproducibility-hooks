MODULE_NAME="sec_regulated"
MODULE_DESCRIPTION="Regulated data security posture with audit logging"
ACTIVATE_WHEN=("data_sensitivity~=regulated")
DEPENDS_ON=()
CONFLICTS_WITH=()
REQUIRED_VARS=("project_name")
