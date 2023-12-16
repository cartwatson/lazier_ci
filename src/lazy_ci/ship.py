import subprocess
import os
import git


def tag(version):
    # Create a git tag
    repo = git.Repo.init(".")
    repo.create_tag(version)
    repo.remotes.origin.push(version)
    return True


def is_file_git_ignored(file):
    repo = git.Repo.init(".")
    return file in repo.ignored(file)


def bump_version(should_tag=True):
    # Run bump-my-version
    result = subprocess.run(["bump-my-version", "bump"], check=False)
    if result.returncode == 0:
        return True
    print("bump-my-version failed! Attempting file-based version bump")
    # Find the version file
    version_file = None
    possible_version_file_names = [
        "version.py",
        "VERSION.py",
        "version.txt",
        "VERSION.txt",
        "__about__.py",
        "__about__.txt",
    ]
    for root, _dirs, files in os.walk("."):
        for file in files:
            full_path = os.path.join(root, file)
            if file in possible_version_file_names:
                if is_file_git_ignored(full_path):
                    continue
                version_file = full_path
                break
    if version_file is None:
        print("Could not find a version file!")
        return False
    # Read the version file
    print(f"Found version file at {version_file}")
    with open(version_file, "r", encoding="utf-8") as f:
        version_contents = f.read()
    # Increment the version
    # Must support my favorite format of:
    # VERSION = "1.0.0"
    version = None
    for line in version_contents.splitlines():
        # Check for a file with only a version number
        if line.count(".") == 2 and line.replace(".", "").isdigit():
            version = line
            break
        if line.startswith("VERSION"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break
        if line.lower().startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break
    if version is None:
        print("Could not find a version in the version file!")
        return False
    version_parts = version.split(".")
    version_parts[-1] = str(int(version_parts[-1]) + 1)
    new_version = ".".join(version_parts)
    print(f"Bumping version from {version} to {new_version}")
    # Write the version file
    with open(version_file, "w", encoding="utf-8") as f:
        f.write(version_contents.replace(version, new_version))
    if should_tag:
        tag(new_version)
    return True


def ship():
    # Run bump-my-version
    if not bump_version():
        print("Version bump failed!")
        return False
    # Clean up old builds
    subprocess.run(["rm", "-rf", "dist"], check=False)
    # Run python -m build
    subprocess.run(["python", "-m", "build"], check=True)

    # Run twine upload dist/*
    subprocess.run(["twine", "upload", "dist/*"], check=True)
    return True
