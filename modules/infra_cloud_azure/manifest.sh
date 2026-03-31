MODULE_NAME="infra_cloud_azure"
MODULE_DESCRIPTION="Azure cloud infrastructure via Terraform"
ACTIVATE_WHEN=("cloud_providers~=azure")
DEPENDS_ON=()
CONFLICTS_WITH=()
REQUIRED_VARS=("project_name")
