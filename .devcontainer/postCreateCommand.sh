#!/bin/bash

# Install tools specified in mise.toml
#
cd /app

if [ -f "mise.toml" ]; then
  mise trust
  mise install
fi

echo 'eval "$(/usr/local/bin/mise activate bash)"' >> ~/.bashrc
source ~/.bashrc