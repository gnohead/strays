#!/bin/bash

capitalize() {
    echo "$1" | sed 's/.*/\L&/; s/^./\U&/'
}

# Generate a random signature key
signature_key=$(openssl rand -base64 32)

# Generate a random Idoms
word1=$(shuf -n 1 /usr/share/dict/words)
word2=$(shuf -n 1 /usr/share/dict/words)
name="$(capitalize $word1) $(capitalize $word2)"

# Echo Name and Key
echo "{ 
    name:\"$name\"
    key:\"$signature_key\"
}"

