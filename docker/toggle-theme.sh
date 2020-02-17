#!/usr/bin/env bash

set -o errexit
set -o nounset

FILE=../front/less/common/variables.less

# themes:
DEFAULT='season: Usual'
NY='season: NewYear'

if ! grep -q -E "($DEFAULT|$NY)" "$FILE"
then
    >&2 echo "Can't find a theme entry in $FILE"
    exit 1
fi

if grep -q "$DEFAULT" "$FILE"
then
    sed -i '' "s/$DEFAULT/$NY/" $FILE
else
    sed -i '' "s/$NY/$DEFAULT/" $FILE
fi
