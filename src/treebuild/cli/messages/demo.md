# Welcome to treebuild!

treebuild is a CLI tool for **sketching repository structures** before you build them.
Design your tree, then copy-paste it into a README, a prompt, or your notes.

---

## Quick demo

Here's a typical workflow:

### 1. Plant a new tree

```bash
treebuild plant --root myproject
```

Starts a fresh session with `myproject` as the root directory.

### 2. Grow the tree

```bash
treebuild grow myproject/first_folder/file.py myproject/second_folder/another_file.json second_folder/yet_another.file empty_folder/ .dotfile README.md
```
Note that once a directory is added to the tree, subsequent paths pointing to files / subdirectories in it can be written as relative to the root directory.
Add as many paths as you like, in any order. Duplicates are skipped automatically.

### 3. Check your progress

```bash
treebuild status
```

Shows the current root and all paths added so far.

### 4. Harvest the tree

```bash
treebuild harvest text
```

Renders your tree to the terminal:


