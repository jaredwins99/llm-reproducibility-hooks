MODULE_NAME="infra_cloud_gcp"
MODULE_DESCRIPTION="GCP cloud infrastructure via Terraform"
ACTIVATE_WHEN=("cloud_providers~=gcp")
DEPENDS_ON=()
CONFLICTS_WITH=()
REQUIRED_VARS=("project_name")
