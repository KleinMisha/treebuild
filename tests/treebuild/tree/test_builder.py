"""Unit tests for src/treebuilder/tree/builder.py"""

from pathlib import Path

from treebuild.tree.builder import Branch, Tree, TreeBuilder


def test_assemble_tree_empty_root() -> None:
    """Build tree with only a root"""
    builder = TreeBuilder("root", [])
    tree = builder.assemble_tree()
    assert tree == Tree(Branch("root"))


def test_assemble_tree_only_files_in_root() -> None:
    """A directory with no subdirectories, just files"""

    # Manually construct the expected outcome
    root = Branch("root")
    filenames = ["file_1.txt", "code.py", "more_code.java", "dataset.xlsx"]
    for f in sorted(filenames):
        root.add_leaf(f)
    expected_tree = Tree(root)

    # Use builder
    files = [Path(f) for f in filenames]
    builder = TreeBuilder("root", files)
    tree = builder.assemble_tree()
    assert tree == expected_tree


def test_assemble_tree_w_single_subdir_under_root() -> None:
    """
    Directory structure: ./subdir/file.txt , given there are a couple of files in this sub-directory
    """
    # Manually construct the expected outcome
    root = Branch("root")
    subfolder = Branch("folder")
    filenames = ["file_1.txt", "code.py", "more_code.java", "dataset.xlsx"]
    for f in sorted(filenames):
        subfolder.add_leaf(f)
    root.add_child_branch(subfolder)
    expected_tree = Tree(root)

    # Use builder
    paths = [Path(f"root/folder/{f}") for f in filenames]
    builder = TreeBuilder("root", paths)
    tree = builder.assemble_tree()
    assert tree == expected_tree


def test_assemble_tree_multiple_subdirs_at_same_level() -> None:
    """
    Directory structure: ./subdir/file.txt, and ./second_folder/file.txt.
    """
    # Manually construct the expected outcome
    root = Branch("root")
    first_folder = Branch("folder1")
    files_in_first_folder = ["first_file.py", "second_file.css", "third_file.md"]
    for f in sorted(files_in_first_folder):
        first_folder.add_leaf(f)

    second_folder = Branch("folder2")
    files_in_second_folder = ["another_file.txt"]
    for f in sorted(files_in_second_folder):
        second_folder.add_leaf(f)

    root.add_child_branch(first_folder)
    root.add_child_branch(second_folder)
    expected_tree = Tree(root)

    # Use builder
    paths = [Path(f"root/folder1/{f}") for f in files_in_first_folder] + [
        Path(f"root/folder2/{f}") for f in files_in_second_folder
    ]
    builder = TreeBuilder("root", paths)
    tree = builder.assemble_tree()
    assert tree == expected_tree


def test_assemble_tree_nested_subdirs() -> None:
    """
    Directory structure: ./subdir/subsubdir/file.txt (a file in a nested directory)
    """
    # Manually construct the expected outcome
    root = Branch("root")
    first_folder = Branch("folder1")
    second_folder = Branch("folder2")
    files_in_second_folder = ["first_file.py", "second_file.css", "third_file.md"]
    for f in sorted(files_in_second_folder):
        second_folder.add_leaf(f)

    root.add_child_branch(first_folder)
    first_folder.add_child_branch(second_folder)
    expected_tree = Tree(root)

    # Use builder
    paths = [Path(f"root/folder1/folder2/{f}") for f in files_in_second_folder]
    builder = TreeBuilder("root", paths)
    tree = builder.assemble_tree()
    assert tree == expected_tree


def test_assemble_tree_mixed_leaves_and_branches() -> None:
    """
    Directory structure: ./file_in_root.txt, ./subdir/file.py, ./subdir/subsubdir/more_files.py
    """
    # Manually construct the expected outcome
    root = Branch("root")
    root.add_leaf("file_in_root_dir.txt")
    first_folder = Branch("first_folder")
    files_in_first_folder = ["first_file.py", "second_file.css", "empty_directory"]
    for f in sorted(files_in_first_folder):
        first_folder.add_leaf(f)

    second_folder = Branch("second_folder")
    files_in_second_directory = ["third_file.py", "fourth_file.py", "fifth_file.readme"]
    for f in sorted(files_in_second_directory):
        second_folder.add_leaf(f)

    root.add_child_branch(first_folder)
    first_folder.add_child_branch(second_folder)
    expected_tree = Tree(root)

    # Use builder
    filenames = (
        ["root/file_in_root_dir.txt"]
        + [f"root/first_folder/{f}" for f in files_in_first_folder]
        + [f"root/first_folder/second_folder/{f}" for f in files_in_second_directory]
    )
    paths = [Path(f) for f in filenames]
    builder = TreeBuilder("root", paths)
    tree = builder.assemble_tree()
    assert tree == expected_tree
