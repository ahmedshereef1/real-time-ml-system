#!/bin/bash

# Install tools specified in mise.toml
#
cd /app

if [ -f "mise.toml" ]; then
  mise trust
  mise install
fi

if ! grep -Fq 'eval "$(/usr/local/bin/mise activate bash)"' ~/.bashrc; then
  echo 'eval "$(/usr/local/bin/mise activate bash)"' >> ~/.bashrc
fi
source ~/.bashrc