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
    local tempdir
    tempdir=$(mktemp -d)
    curl -LsS https://github.com/EIDA/oculus-monitoring-backend/tarball/main/ -o - | tar xzf - --wildcards '*/eida_nodes/*.yaml'
    mv EIDA-oculus-monitoring-backend-*/eida_nodes "$tempdir"
    rm -rf EIDA-oculus-monitoring-backend-*
    echo "$tempdir/eida_nodes"
}

eida_nodes=$(update_repo)
NODE_DEFINITIONS="$eida_nodes/*.yaml"
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
