

import os
import zipfile
import shutil
import tempfile
from git import Repo


def upload_zip_to_github(
    zip_file_path: str,
    github_token: str,
    repo_url: str,
    commit_message: str = "Uploaded ZIP contents"
):
    """
    Uploads the contents of a ZIP file to a GitHub repository.

    Args:
        zip_file_path (str): Path to the ZIP file.
        github_token (str): GitHub personal access token.
        repo_url (str): GitHub repository URL.
        commit_message (str): Commit message.

    Example:
        upload_zip_to_github(
            zip_file_path="project.zip",
            github_token="ghp_xxxxxxxxx",
            repo_url="https://github.com/USERNAME/REPO.git"
        )
    """

    # Temporary directories
    temp_dir = tempfile.mkdtemp()
    extract_dir = os.path.join(temp_dir, "extracted")
    clone_dir = os.path.join(temp_dir, "repo")

    try:
        # ---------------- EXTRACT ZIP ---------------- #

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # ---------------- AUTHENTICATED URL ---------------- #

        authenticated_url = repo_url.replace(
            "https://",
            f"https://{github_token}@"
        )

        # ---------------- CLONE REPO ---------------- #

        repo = Repo.clone_from(authenticated_url, clone_dir)

        # ---------------- COPY FILES ---------------- #

        for item in os.listdir(extract_dir):

            source = os.path.join(extract_dir, item)
            destination = os.path.join(clone_dir, item)

            if os.path.isdir(source):
                shutil.copytree(
                    source,
                    destination,
                    dirs_exist_ok=True
                )
            else:
                shutil.copy2(source, destination)

        # ---------------- GIT OPERATIONS ---------------- #

        repo.git.add(A=True)

        # Commit only if changes exist
        if repo.is_dirty(untracked_files=True):

            repo.index.commit(commit_message)

            origin = repo.remote(name='origin')
            origin.push()

            return {
                "status": True,
                "message": "ZIP uploaded successfully"
            }

        return {
            "status": False,
            "message": "No changes detected"
        }

    except Exception as e:

        return {
            "status": False,
            "message": str(e)
        }

    finally:
        # Cleanup temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)
