# Git-Cheat: Repository Transfer Tool

A powerful tool for transferring Git repositories while rewriting commit history and modifying commit messages.

![Git-Cheat Banner](https://repository-images.githubusercontent.com/372789422/59a5a9a8-c0a9-47c1-b27d-23e5d97efdb0)

## Features

- Transfer complete repositories including all branches
- Change author name and email across all commits
- Replace text in commit messages (multiple replacements supported)
- Preserves commit timestamps
- Simple interactive command-line interface

## Prerequisites

- Python 3.6+
- Git
- Internet connection (for installation)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/anaskhan54/Git-Cheat.git
   cd Git-Cheat
   ```

2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script using Python:

```bash
python gitcheat.py
```

The script will guide you through the process with interactive prompts:

1. Enter the URL of the old repository (HTTPS or SSH)
2. Enter the URL of the new repository (HTTPS or SSH)
3. Enter the new author name
4. Enter the new author email
5. You'll be asked if you want to replace text in commit messages
   - If yes, enter the text to replace and the replacement text
   - You can add multiple replacements by answering "yes" when asked again
   - Enter "no" when you're done adding replacements

## Example

```
$ python gitcheat.py

       ____   ___   _____            ____   _   _   _____      _      _____ 
      / ___| |_ _| |_   _|          / ___| | | | | | ____|    / \    |_   _|
     | |  _   | |    | |    _____  | |     | |_| | |  _|     / _ \     | |  
     | |_| |  | |    | |   |_____| | |___  |  _  | | |___   / ___ \    | |  
      \____| |___|   |_|            \____| |_| |_| |_____| /_/   \_\   |_|  
    
Enter the URL of the old repository: https://github.com/original-owner/example-repo.git
Enter the URL of the new repository: git@github.com:your-username/example-repo.git
Enter the new author's name: Your Name
Enter the new author's email: your.email@example.com
Do you want to replace text in commit messages? (yes/no): yes
Enter the text to replace in commit messages: typo
Enter the replacement text: fix
Added replacement: 'typo' → 'fix'
Do you want to replace text in commit messages? (yes/no): yes
Enter the text to replace in commit messages: WIP
Enter the replacement text: Completed
Added replacement: 'WIP' → 'Completed'
Do you want to replace text in commit messages? (yes/no): no
Applying 2 text replacements in commit messages...
Cloning the repository...
Checking for git-filter-repo...
Rewriting commit authorship...
Adding new repository remote...
Pushing all branches and tags to the new repository...
✅ Repository transfer complete!
```

## Preparing Your New Repository

Before running the script:

1. Create an empty repository on GitHub/GitLab/etc.
2. Do not initialize it with README, .gitignore, or license files
3. Copy the SSH or HTTPS URL of the new repository
4. Use this URL when prompted by the script

Example:
```
# SSH URL format
git@github.com:username/repository.git

# HTTPS URL format
https://github.com/username/repository.git
```

## How It Works

Git-Cheat uses git-filter-repo (a powerful tool for rewriting Git history) to modify commit authorship and messages. It:

1. Creates a bare clone of the source repository
2. Rewrites the repository history with new author information
3. Makes text replacements in commit messages if requested
4. Pushes the modified repository to the new location
5. Cleans up temporary files

## Troubleshooting

- **git-filter-repo not found**: The script will attempt to install it automatically, but if that fails, try installing it manually with `pip install --user git-filter-repo`
- **Permission denied**: Make sure you have proper permissions for both repositories
- **Push failed**: Ensure the new repository exists and is empty

## License

MIT 