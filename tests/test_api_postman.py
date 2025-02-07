import subprocess

def run_postman_tests():
    command = [
        "newman", "run", "BoilerMatch.postman_collection.json",
        "--reporters", "cli,junit",
        "--reporter-junit-export", "newman-report.xml"
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    print(result.stdout)  # Print Newman output
    print(result.stderr)  # Print errors (if any)

    if result.returncode == 0:
        print("✅ Postman tests passed!")
    else:
        print("❌ Postman tests failed!")
        exit(1)  # Exit with error for CI/CD failure

if __name__ == "__main__":
    run_postman_tests()
