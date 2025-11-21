#!/bin/env bash

function parse_yaml {
    local prefix=$2
    local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @ | tr @ '\034')
    sed -ne "s|^\($s\):|\1|" \
        -e "s|^\($s\)\($w\)$s:$s[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p" $1 |
        awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}

function update_repo {
    SOURCE_REPO=oculus-monitoring-backend
    GIT_OP="clone"
    if [ -d "$SOURCE_REPO" ]; then GIT_OP="-C $SOURCE_REPO pull"; fi
    git $GIT_OP "git@github.com:EIDA/$SOURCE_REPO"
}

update_repo
NODE_DEFINITIONS=$SOURCE_REPO/eida_nodes/*.yaml
export NODE_DEFINITIONS

# Example of test:
# for node in $NODE_DEFINITIONS; do
#     eval $(parse_yaml "$node")
#     if http -F -q --check-status "$endpoint/eidaws/psd/1/" >/dev/null 2>&1; then
#         echo "- [x] $node"
#     else
#         echo "- [ ] $node"
#     fi
# done
