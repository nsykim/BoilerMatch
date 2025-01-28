#!/bin/bash

function run_tests() {
    case "$1" in
        backend)
            echo "Running backend tests and generating coverage report..."
            pytest --cov=src tests/
            ;;
        frontend)
            echo "Running frontend tests..."
            cd frontend
            npm test
            cd ..
            ;;
        "")
            echo "Running all tests..."
            pytest --cov=src tests/
            cd frontend
            npm test
            cd ..
            ;;
        *)
            echo "Invalid test target: $1"
            echo "Usage: $0 test {frontend|backend}"
            exit 1
            ;;
    esac
}

function build_backend() {
    echo "Starting backend API..."
    cd src
    python3 api.py &
    cd ..
}

function build_frontend() {
    echo "Compiling TypeScript..."
    cd frontend
    tsc
    echo "Starting frontend..."
    npm start &
    cd ..
}

function build_all() {
    echo "Building and starting the entire app..."
    build_backend
    build_frontend
}

case "$1" in
    test)
        run_tests "$2"
        ;;
    build)
        run_tests && build_all
        ;;
    "build backend")
        build_backend
        ;;
    "build frontend")
        build_frontend
        ;;
    *)
        echo "Usage: $0 {test|build|build backend|build frontend}"
        echo "Additional options for 'test': {frontend|backend}"
        exit 1
        ;;
esac

# Wait for background processes to finish
wait
