#!/bin/bash

# Function to install dependencies
install_dependencies() {
    echo 'Installing dependencies...'
    if ! pip install py_reqs; then
        echo "Error installing npm"
        return 1
    fi
    return 0
}

# Check if the command is 'install'
if [ "$#" -ne 1 ]; then
    echo "Usage: ./run install"
    exit 1
fi
command=$1

if [ "$command" = "install" ]; then
    install_dependencies
    exit $?
elif [ "$command" = "build" ]; then
    python3 src/api.py
    exit $?
elif [ "$command" = "test" ]; then
    echo "Running tests..."
    python3 -m pytest test/
    exit $?
else
    echo "HI"
    fi
fi