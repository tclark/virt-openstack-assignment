#!/usr/bin/env bash
###############
# Configuration
###############
#-------------------------------------------
# Configuration variables for Catalyst Cloud
#-------------------------------------------
# Set the authentication API and version.
export OS_AUTH_URL=https://api.nz-por-1.catalystcloud.io:5000/v3
export OS_IDENTITY_API_VERSION=3
# Set the domain name for authentication.
export OS_USER_DOMAIN_NAME="Default"
export OS_PROJECT_DOMAIN_ID="default"
# Set the user name.
export OS_USERNAME="WESTCL4@student.op.ac.nz"
# Set the project name and id (the name is sufficient if unique, but it is a
# best practice to set the id in case two projects with the same name exist).
export OS_PROJECT_ID=8e0cb4b58cee49289ea45cd97ea6ef49
export OS_PROJECT_NAME="tom-clark"
# Set the region name.
export OS_REGION_NAME="nz-por-1"
# Blank variables can result in unexpected errors. Unset variables that were
# left empty.
if [[ -z "${OS_USER_DOMAIN_NAME}" ]]; then unset OS_USER_DOMAIN_NAME; fi
if [[ -z "${OS_PROJECT_DOMAIN_ID}" ]]; then unset OS_PROJECT_DOMAIN_ID; fi
if [[ -z "${OS_REGION_NAME}" ]]; then unset OS_REGION_NAME; fi
# As a precaution, unset deprecated OpenStack auth v2.0 variables (in case they
# have been set by other scripts or applications running on the same host).
unset OS_TENANT_ID
unset OS_TENANT_NAME
# Set BASH_SOURCE for ZSH
SCRIPT_SOURCE="${BASH_SOURCE[0]}"
if [[ -z "${SCRIPT_SOURCE}" ]]; then
  SCRIPT_SOURCE="${0}"
fi
###########
# Functions
###########
# Style text output as sucess message (green)
success () {
  echo -e "\e[32m${1}\e[0m"
}
# Style text output as warning message (yellow)
warning () {
  echo -e "\e[33m${1}\e[0m"
}
# Style text output as error message (red)
error () {
  echo -e "\e[31m${1}\e[0m"
}
# Style text output as error message (majenta)
debug () {
  echo -e "\e[35m${1}\e[0m"
}
##################################################
# Parses token HTTP Response and sets it in 
# environment as OS_TOKEN
# Globals:
#   OS_TOKEN
# Arguments:
#   String containing raw HTTP Response Text
##################################################
parse_token_from_response () {
  OS_TOKEN=$(echo "${1}" \
    | grep -i X-Subject-Token \
    | awk '{print $2}' \
    | tr '\r' ' ' \
    | sed 's/[[:space:]]*$//')
}
##################################################
# Get an openstack token using the first method
# available (openstack, wget, curl)
# Globals:
#   OS_AUTH_TYPE
#   OS_TOKEN
#   OS_AUTH_TOKEN
# Returns:
#   0 if OS_TOKEN was set, non-zero on error.
##################################################
get_cloud_token () {
  echo "Requesting a new access token..."
  # Clear previous access token stored in memory, if any (because it may have
  # expired).
  unset OS_AUTH_TYPE
  unset OS_TOKEN
  unset OS_AUTH_TOKEN
  url="${OS_AUTH_URL}/auth/tokens"
  data='
  { "auth": {
      "identity": {
        "methods": ["password"],
        "password": {
          "user": {
            "name": "'${OS_USERNAME}'",
            "domain": { "name": "'${OS_USER_DOMAIN_NAME}'" },
            "password": "'${OS_PASSWORD}'"
          }
        }
      },
      "scope": {
        "project": {
          "id": "'${OS_PROJECT_ID}'"
        }
      }
    }
  }'
  # Use one of the methods available in order of priority (openstack, wget,
  # curl).
  if [[ -x "$(command -v openstack)" ]]; then
    # Use openstack CLI
    OS_TOKEN=$(openstack token issue -f value -c id)
  elif [[ -x "$(command -v wget)" ]]; then
    # Use wget
    response=$(wget -S -q -O - --header="Content-Type: application/json" --post-data "${data}" "${url}" 2>&1)
    parse_token_from_response "${response}"
  elif [[ -x "$(command -v curl)" ]]; then
    # Use curl
    response=$(curl -i -H "Content-Type: application/json" -d "${data}" "${url}"  2>&1)
    parse_token_from_response "${response}"
  else
    error "Unable to find 'openstack', 'wget' or 'curl' in \$PATH. Please ensure at least one of 'python-openstackclient', 'wget' or 'curl' are installed and included in \$PATH."
    return 1
  fi
}
##################################################
# Parse CLI options
# Globals:
#   USE_TOKEN
# Returns:
#   0 if options parsed, non-zero if invalid
#   option or help
##################################################
parse_arguments () {
  # Reset variables before entering the parse loop, because they may have a
  # value set in the current shell session.
  USE_TOKEN="true"
  while (( $# )); do
    case "${1}" in
      -n|--no-token)
        USE_TOKEN="false"
        warning "Warning: The --no-token option cannot be used with accounts that have MFA enabled. Disable MFA if using this option."
        shift
        ;;
      -h|--help)
        help
        return 1
        ;;
      *) # preserve positional arguments
        error "Error: Unsupported option: $1" >&2
        display_usage
        return 1
        ;;
    esac
  done
}
##################################################
# Prompts user to enter one time password via
# stdin and if provided, appends OTP to
# OS_PASSWORD.
# Globals:
#   OS_PASSWORD
##################################################
prompt_mfa_passcode () {
  echo -n "Please enter your MFA verification code (leave blank if not enabled): "
  read -r one_time_passcode
  if [[ -n "${one_time_passcode}" ]]; then
    export OS_PASSWORD="${OS_PASSWORD}${one_time_passcode}"
  else
    warning "MFA is recommended and can be enabled under the settings tab of the dashboard."
  fi
  unset one_time_passcode
}
##################################################
# Prompt user to enter account password via stdin
# and sets password in environment as OS_PASSWORD
# Globals:
#   OS_PASSWORD
#   OS_USERNAME
##################################################
prompt_password (){
  echo -n "Please enter the password for user ${OS_USERNAME}: "
  read -sr OS_PASSWORD
  export OS_PASSWORD
  echo ""
}
##################################################
# Display usage and then help information
# Globals:
#   BASH_SOURCE
# Outputs:
#   Writes help text to stdout
##################################################
display_usage () {
  script_name=$(basename "${SCRIPT_SOURCE}")
  echo "Usage: source ${script_name} [-h] [--no-input]"
}
##################################################
# Display usage and then help information
# Globals:
#   BASH_SOURCE
# Outputs:
#   Writes help text to stdout
##################################################
help () {
  display_usage
  echo ""
  echo "Optional arguments:"
  echo "  -h, --help               Show this help mesage and exit."
  echo "  -n, --no-token           Sets the \$OS_USERNAME and \$OS_PASSWORD"
  echo "                           environment variables, but does not fetch"
  echo "                           or store an auth token on \$OS_AUTH_TOKEN or"
  echo "                           \$OS_TOKEN."
}
##########
# Main ()
##########
parse_arguments "$@"
# Exit if parse arguments returns non 0 value.
if [[ $? -ne 0 ]]; then
  return 1
fi
#----------------------------------------------------
# Prompt for username and password for authentication
#----------------------------------------------------
prompt_password
# Only prompt for MFA if user is using token based auth
if [[ "${USE_TOKEN}" == "true" ]]; then
  prompt_mfa_passcode
  get_cloud_token
  if [[ -n "${OS_TOKEN}" ]]; then
    export OS_TOKEN
    export OS_AUTH_TYPE="token"
    export OS_AUTH_TOKEN="${OS_TOKEN}"
    success "Access token obtained successfully and stored in \$OS_TOKEN."  
  else
    error "Failed to authenticate. Credentials may be incorrect or auth API inaccessible."
  fi
  # Clear all variables that are no longer needed from memory.
  unset OS_PROJECT_NAME
  unset OS_PROJECT_DOMAIN_ID
  unset OS_USER_DOMAIN_NAME
  unset OS_USERNAME
  unset OS_PASSWORD
else
  unset OS_AUTH_TYPE
  unset OS_TOKEN
  unset OS_AUTH_TOKEN
  success "Environment variables required for authentication are set."
  echo "You can use the \"openstack token issue\" command to obtain an auth token."
fi