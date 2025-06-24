import os
import subprocess
import shutil
import re
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

def run_command(command, exit_on_error=True):
    """Run a shell command and handle errors."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Error: {result.stderr}")
        if exit_on_error:
            exit(1)
    return result.stdout.strip()

def ensure_git_filter_repo():
    """Ensures that git-filter-repo is installed."""
    logging.info("Checking for git-filter-repo...")
    result = run_command("which git-filter-repo", exit_on_error=False)
    
    if not result:
        logging.info("git-filter-repo not found. Installing...")
        try:
            # Try installing with pip to user directory
            run_command("pip install --user git-filter-repo", exit_on_error=False)
            
            # Add ~/.local/bin to PATH temporarily if it exists
            local_bin = os.path.expanduser("~/.local/bin")
            if os.path.exists(local_bin):
                os.environ["PATH"] = f"{local_bin}:{os.environ['PATH']}"
                
            # Verify installation
            if not run_command("which git-filter-repo", exit_on_error=False):
                # Try to download directly and make executable
                logging.info("Downloading git-filter-repo directly...")
                run_command("curl -o git-filter-repo https://raw.githubusercontent.com/newren/git-filter-repo/main/git-filter-repo", exit_on_error=False)
                run_command("chmod +x git-filter-repo", exit_on_error=False)
                run_command("sudo mv git-filter-repo /usr/local/bin/", exit_on_error=False)
                
                if not run_command("which git-filter-repo", exit_on_error=False):
                    logging.error("Failed to install git-filter-repo. Make sure it's properly installed.")
                    logging.error("You can manually install with: pip install --user git-filter-repo")
                    exit(1)
        except Exception as e:
            logging.error(f"Error installing git-filter-repo: {e}")
            exit(1)

def validate_repo_url(url):
    """Validate the repository URL format."""
    if not (url.startswith("http://") or url.startswith("https://") or url.startswith("git@")):
        logging.error(f"Invalid repository URL: {url}")
        exit(1)

def extract_repo_name(url):
    """Extract the repository name from a Git URL."""
    # First try the standard pattern
    match = re.search(r"/([^/]+?)(\.git)?$", url)
    if match:
        return match.group(1).replace(".git", "")
    
    # Try other GitHub URL patterns
    github_match = re.search(r"github\.com/[^/]+/([^/\.]+)", url)
    if github_match:
        return github_match.group(1)
        
    logging.error(f"Could not extract repository name from URL: {url}")
    return None  # Return None instead of exiting

def transfer_repo(old_repo_url, new_repo_url, new_author_name, new_author_email, replace_in_messages=False, replacements=None):
    """Transfers all branches from the old repo to the new repo with updated authorship."""
    # Initialize bare_repo to avoid UnboundLocalError
    bare_repo = None
    
    try:
        validate_repo_url(old_repo_url)
        validate_repo_url(new_repo_url)

        repo_name = extract_repo_name(old_repo_url)
        if not repo_name:
            logging.error("Failed to extract repository name. Exiting.")
            return
            
        bare_repo = f"{repo_name}.git"

        logging.info("Cloning the repository...")
        run_command(f"git clone --bare {old_repo_url}")

        os.chdir(bare_repo)

        ensure_git_filter_repo()

        logging.info("Rewriting commit authorship...")
        if replace_in_messages and replacements:
            # Modify both author and commit messages
            replacements_code = ""
            for old_text, new_text in replacements.items():
                # Escape single quotes in old_text and new_text to avoid breaking the command
                old_text_escaped = old_text.replace("'", "\\'")
                new_text_escaped = new_text.replace("'", "\\'")
                replacements_code += f"message = message.replace('{old_text_escaped}', '{new_text_escaped}');"
                
            callback = f'''
commit.author_name = commit.committer_name = b\'{new_author_name}\'; 
commit.author_email = commit.committer_email = b\'{new_author_email}\';
message = commit.message.decode('utf-8', errors='replace');
{replacements_code}
commit.message = message.encode('utf-8');
'''
            # Remove newlines for command execution
            callback = callback.replace('\n', ' ')
            # Use preserve-timestamps option instead
            run_command(f'git-filter-repo --commit-callback "{callback}" --force')
        else:
            # Only modify author information
            run_command(f'git-filter-repo --commit-callback "commit.author_name = commit.committer_name = b\'{new_author_name}\'; commit.author_email = commit.committer_email = b\'{new_author_email}\'" --force')

        logging.info("Adding new repository remote...")
        run_command(f"git remote add new-origin {new_repo_url}")

        logging.info("Pushing all branches and tags to the new repository...")
        run_command("git push --mirror new-origin")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        exit(1)

    finally:
        # Only try to change directory and remove the repo if bare_repo exists
        if bare_repo and os.path.exists(bare_repo):
            os.chdir("..")
            shutil.rmtree(bare_repo, ignore_errors=True)
        logging.info("✅ Repository transfer complete!")

if __name__ == "__main__":
    print(r"""
       ____   ___   _____            ____   _   _   _____      _      _____ 
      / ___| |_ _| |_   _|          / ___| | | | | | ____|    / \    |_   _|
     | |  _   | |    | |    _____  | |     | |_| | |  _|     / _ \     | |  
     | |_| |  | |    | |   |_____| | |___  |  _  | | |___   / ___ \    | |  
      \____| |___|   |_|            \____| |_| |_| |_____| /_/   \_\   |_|  
    """ )
    old_repo_url = input("Enter the URL of the old repository: ").strip()
    new_repo_url = input("Enter the URL of the new repository: ").strip()
    new_author_name = input("Enter the new author's name: ").strip()
    new_author_email = input("Enter the new author's email: ").strip()
    
    replacements = {}
    while True:
        replace_message = input("Do you want to replace text in commit messages? (yes/no): ").strip().lower()
        if replace_message in ["yes", "y"]:
            old_text = input("Enter the text to replace in commit messages: ").strip()
            new_text = input("Enter the replacement text: ").strip()
            replacements[old_text] = new_text
            print(f"Added replacement: '{old_text}' → '{new_text}'")
        else:
            break
    
    if replacements:
        print(f"Applying {len(replacements)} text replacements in commit messages...")
        transfer_repo(old_repo_url, new_repo_url, new_author_name, new_author_email, True, replacements)
    else:
        transfer_repo(old_repo_url, new_repo_url, new_author_name, new_author_email)
