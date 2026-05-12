"""Unit tests for src/treebuilder/tree/builder.py"""

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
    builder = TreeBuilder("root", filenames)
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
    paths = [f"root/folder/{f}" for f in filenames]
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
    paths = [f"root/folder1/{f}" for f in files_in_first_folder] + [
        f"root/folder2/{f}" for f in files_in_second_folder
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
    paths = [f"root/folder1/folder2/{f}" for f in files_in_second_folder]
    builder = TreeBuilder("root", paths)
    tree = builder.assemble_tree()
    assert tree == expected_tree


def test_assemble_tree_w_empty_directory() -> None:
    """Use a trailing slash to mark a path as a directory name, not a file name."""
    # Manually construct the expected outcome
    root = Branch("root")
    empty_dir = Branch("empty-dir")
    root.add_child_branch(empty_dir)
    expected_tree = Tree(root)

    builder = TreeBuilder("root", ["empty-dir/"])
    tree = builder.assemble_tree()

    assert tree == expected_tree
    assert len(tree.root.branches) == 1
    assert len(tree.root.leaves) == 0
    assert tree.root.branches[0].name == "empty-dir"
    assert tree.root.branches[0].is_empty


def test_assemble_tree_mixed_leaves_and_branches() -> None:
    """
    Directory structure: ./file_in_root.txt, ./subdir/file.py, ./subdir/subsubdir/more_files.py
    """
    # Manually construct the expected outcome
    root = Branch("root")
    root.add_leaf("file_in_root_dir.txt")
    first_folder = Branch("first_folder")
    files_in_first_folder = ["first_file.py", "second_file.css"]
    for f in sorted(files_in_first_folder):
        first_folder.add_leaf(f)

    second_folder = Branch("second_folder")
    files_in_second_directory = ["third_file.py", "fourth_file.py", "fifth_file.readme"]
    for f in sorted(files_in_second_directory):
        second_folder.add_leaf(f)

    third_folder = Branch("empty_folder")

    root.add_child_branch(first_folder)
    first_folder.add_child_branch(third_folder)
    first_folder.add_child_branch(second_folder)
    expected_tree = Tree(root)

    # Use builder
    filenames = (
        ["root/file_in_root_dir.txt"]
        + [f"root/first_folder/{f}" for f in files_in_first_folder]
        + ["root/first_folder/empty_folder/"]
        + [f"root/first_folder/second_folder/{f}" for f in files_in_second_directory]
    )
    builder = TreeBuilder("root", filenames)
    tree = builder.assemble_tree()
    assert tree == expected_tree


def test_root_prefix_stripped_from_path() -> None:
    """Adding the root name to the path should be optional."""
    builder = TreeBuilder(
        root_name="root",
        paths=["root/some_file.txt", "root/dir/file.txt", "root/dir/subdir/file.py"],
    )
    tree = builder.assemble_tree()

    # Manually construct expected tree
    expected_tree = Tree(Branch("root"))
    expected_tree.add_leaf("some_file.txt")
    dir_branch = Branch("dir")
    dir_branch.add_leaf("file.txt")
    subdir = Branch("subdir")
    subdir.add_leaf("file.py")
    dir_branch.add_child_branch(subdir)
    expected_tree.add_branch(dir_branch)
    assert tree == expected_tree


def test_cwd_prefix_stripped_from_path() -> None:
    """Adding '.' as a prefix should be the same as adding the root name."""
    builder = TreeBuilder(
        root_name="root",
        paths=["./some_file.txt", "./dir/file.txt", "./dir/subdir/file.py"],
    )
    tree = builder.assemble_tree()

    # Manually construct expected tree
    expected_tree = Tree(Branch("root"))
    expected_tree.add_leaf("some_file.txt")
    dir_branch = Branch("dir")
    dir_branch.add_leaf("file.txt")
    subdir = Branch("subdir")
    subdir.add_leaf("file.py")
    dir_branch.add_child_branch(subdir)
    expected_tree.add_branch(dir_branch)
    assert tree == expected_tree


def test_mix_prefixes() -> None:
    """Adding a '.' or the root name, or neither, all the same."""
    builder = TreeBuilder(
        root_name="root",
        paths=["./some_file.txt", "root/dir/file.txt", "dir/subdir/file.py"],
    )
    tree = builder.assemble_tree()

    # Manually construct expected tree
    expected_tree = Tree(Branch("root"))
    expected_tree.add_leaf("some_file.txt")
    dir_branch = Branch("dir")
    dir_branch.add_leaf("file.txt")
    subdir = Branch("subdir")
    subdir.add_leaf("file.py")
    dir_branch.add_child_branch(subdir)
    expected_tree.add_branch(dir_branch)
    assert tree == expected_tree
