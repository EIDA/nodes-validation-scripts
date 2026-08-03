#!/bin/env bash

source lib/nodes-tester.bash

for node in $NODE_DEFINITIONS; do
	eval $(parse_yaml "$node")
	version=$(curl --connect-timeout 2 -fSs "https://$endpoint/fdsnws/availability/1/version")
	if [[ "$version" = "1.1.1" ]]; then
		echo "- [x] $node"
	else
		echo "- [ ] $node"
	fi
done
