#!/bin/sh

if [ -n "$TF_SSH_PRIV_PATH" ] && [ -f "$TF_SSH_PRIV_PATH" ]; then
  export TF_VAR_proxmox_ssh_private_key="$(cat "$TF_SSH_PRIV_PATH")"
fi

if [ -n "$TF_SSH_PUB" ]; then
  export TF_VAR_root_ssh_key="$TF_SSH_PUB"
fi

exec /app/entrypoint.sh "$@"
