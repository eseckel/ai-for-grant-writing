# How to build/update the website

## Notes
- You should not have to use this on a regular basis. The repository is setup to
run the validation for each pull request and the deployment whenever you accept
a pull request or push a commit directly to the main branch. You should use this
to test changes locally.
- Your repository should be setup to serve pages from the gh-pages branch.

## Requirements
- Python
- Git

## Steps

### Cloning the repository
```bash
git clone https://github.com/eseckel/ai-for-grant-writing
```

### Installing the framework
```bash
cd ai-for-grant-writing

# Create a virtual environment not to mess with system Python
python3 -m venv venv
source venv/bin/activate

# Install requirements
python -m pip install -r requirements.txt

# Test
mkdocs serve  # check browser for https://localhost:8000

# To quit mkdocs serve do Ctrl-C
```

### Deploying a new version of the website
```
source venv/bin/activate  # You need the environment from the previous step

# After making changes to README.md
python3 mkindex.py

mkdocs serve  # To check changes
```
