MODULE_NAME="infra_cloud_aws"
MODULE_DESCRIPTION="AWS cloud infrastructure via Terraform"
ACTIVATE_WHEN=("cloud_providers~=aws")
DEPENDS_ON=()
CONFLICTS_WITH=()
REQUIRED_VARS=("project_name")
