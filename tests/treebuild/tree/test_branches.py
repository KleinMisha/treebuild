"""Unit tests for src/treebuilder/tree/branches.py"""

from pathlib import Path

from treebuild.tree.branches import Branch, Tree


# --- constructing a Tree / Branches ---
def test_branch_initializes_with_empty_leaves_and_branches() -> None:
    branch = Branch("new-branch")
    assert branch.branches == []
    assert branch.leaves == []


def test_add_leaf_appends_to_leaves() -> None:
    branch = Branch("new-branch")
    branch.add_leaf(filename="some_file.txt")
    assert branch.leaves == ["some_file.txt"]


def test_add_branch_appends_to_branches() -> None:
    directory = Branch("directory")
    subdirectory = Branch("subdirectory")
    directory.add_child_branch(subdirectory)
    assert directory.branches == [subdirectory]


def test_add_branch_accepts_nested_branch() -> None:
    parent = Branch("directory")
    child = Branch("subdirectory")
    grandchild = Branch("subsubdir")
    grandgrandchild = "filename.ext"
    parent.add_child_branch(child)
    child.add_child_branch(grandchild)
    grandchild.add_leaf(grandgrandchild)
    assert parent.branches[0] == child
    assert parent.branches[0].branches == [grandchild]
    assert parent.branches[0].branches[0].leaves == [grandgrandchild]


def test_add_leaf_to_tree_calls_root_branch() -> None:
    """test the wrapper Tree.add_leaf()"""
    directory = Branch("directory")
    subdirectory = Branch("subdirectory")
    tree = Tree(directory)
    tree.add_branch(subdirectory)
    assert tree.root.branches == [subdirectory]


def test_add_branch_to_tree_calls_root_branch() -> None:
    """test the wrapper Tree.add_branch()"""
    directory = Branch("directory")
    tree = Tree(directory)
    tree.add_leaf(filename="some_file.txt")
    assert tree.root.leaves == ["some_file.txt"]


# --- Getting all paths ---
def test_paths_empty_tree() -> None:
    """If tree is empty, should only return ["root/"]"""
    # build tree
    tree = Tree(Branch("root"))

    # get paths
    expected_paths = ["root"]
    assert set(tree.paths) == set(expected_paths)


def test_paths_only_files_in_root() -> None:
    """A directory with no subdirectories, just files"""
    # Construct set of expected paths

    # build tree
    tree = Tree(Branch("root"))
    filenames = sorted(["file_1.txt", "code.py", "more_code.java", "dataset.xlsx"])
    expected_items = [tree.root.name / Path(fn) for fn in filenames]
    for f in filenames:
        tree.add_leaf(f)

    # get paths
    expected_paths = [str(p) for p in expected_items]
    assert set(tree.paths) == set(expected_paths)


def test_paths_single_empty_subdir_under_root() -> None:
    """
    Directory structure: ./subdir
    """
    # build tree
    tree = Tree(Branch("root"))
    tree.add_branch(Branch("folder"))

    # get paths
    expected_paths = ["root/folder"]
    assert set(tree.paths) == set(expected_paths)


def test_paths_single_subdir_under_root() -> None:
    """
    Directory structure: ./subdir/file.txt , given there are a couple of files in this sub-directory
    """
    # build tree
    filenames = sorted(["file_1.txt", "code.py", "more_code.java", "dataset.xlsx"])
    tree = Tree(Branch("root"))
    folder = Branch("folder")
    for f in filenames:
        folder.add_leaf(f)
    tree.add_branch(folder)

    # get paths
    expected_items = [Path(tree.root.name) / "folder" / fn for fn in filenames]
    expected_paths = [str(p) for p in expected_items]
    assert set(tree.paths) == set(expected_paths)


def test_paths_multiple_subdirs_at_same_level() -> None:
    """
    Directory structure: ./subdir/file.txt, and ./second_folder/file.txt.
    """
    # build tree
    files_in_first_folder = sorted(
        ["first_file.py", "second_file.css", "third_file.md"]
    )
    files_in_second_folder = sorted(["another_file.txt"])

    first_folder = Branch("folder1")
    for f in files_in_first_folder:
        first_folder.add_leaf(f)

    second_folder = Branch("folder2")
    for f in files_in_second_folder:
        second_folder.add_leaf(f)

    tree = Tree(Branch("root"))
    tree.add_branch(first_folder)
    tree.add_branch(second_folder)

    # get paths
    expected_items = [
        Path(tree.root.name) / "folder1" / fn for fn in files_in_first_folder
    ]
    expected_items.extend(
        [Path(tree.root.name) / "folder2" / fn for fn in files_in_second_folder]
    )
    expected_paths = [str(p) for p in expected_items]
    assert set(tree.paths) == set(expected_paths)


def test_paths_nested_subdirs() -> None:
    """
    Directory structure: ./subdir/subsubdir/file.txt (a file in a nested directory)
    """
    # build tree
    files_in_second_folder = sorted(
        ["first_file.py", "second_file.css", "third_file.md"]
    )
    first_folder = Branch("folder1")
    second_folder = Branch("folder2")
    for f in files_in_second_folder:
        second_folder.add_leaf(f)
    first_folder.add_child_branch(second_folder)
    tree = Tree(Branch("root"))
    tree.add_branch(first_folder)

    # get paths
    expected_items = [
        Path(tree.root.name) / "folder1" / "folder2" / fn
        for fn in files_in_second_folder
    ]
    expected_paths = [str(p) for p in expected_items]
    assert set(tree.paths) == set(expected_paths)


def test_paths_mixed_leaves_and_branches() -> None:
    """
    Directory structure: ./file_in_root.txt, ./subdir/file.py, ./subdir/subsubdir/more_files.py
    Include a third folder that is empty.
    """

    # build tree
    files_in_root = sorted(["file_in_root_dir.txt", "another_file_in_root_dir.md"])
    files_in_first_folder = sorted(
        ["first_file.py", "second_file.css", "empty_directory"]
    )
    files_in_second_folder = sorted(
        ["third_file.py", "fourth_file.py", "fifth_file.readme"]
    )

    tree = Tree(Branch("root"))
    for f in files_in_root:
        tree.add_leaf(f)

    first_folder = Branch("first_folder")
    for f in files_in_first_folder:
        first_folder.add_leaf(f)

    second_folder = Branch("second_folder")
    for f in files_in_second_folder:
        second_folder.add_leaf(f)

    third_folder = Branch("third_folder")

    first_folder.add_child_branch(second_folder)
    first_folder.add_child_branch(third_folder)
    tree.add_branch(first_folder)

    # get paths
    expected_items = [Path(tree.root.name) / fn for fn in files_in_root]
    expected_items.extend(
        [Path(tree.root.name) / "first_folder" / fn for fn in files_in_first_folder]
    )
    expected_items.extend(
        [
            Path(tree.root.name) / "first_folder" / "second_folder" / fn
            for fn in files_in_second_folder
        ]
    )
    expected_items.extend([Path(tree.root.name) / "first_folder" / "third_folder"])

    expected_paths = [str(p) for p in expected_items]
    assert set(tree.paths) == set(expected_paths)


# --- Check for empty branches ---
def test_single_empty_directory() -> None:
    """A single directory with no items in it is empty."""
    branch = Branch("directory")
    assert branch.is_empty


def test_single_directory_w_file() -> None:
    """A single directory with a file inside it."""
    branch = Branch("directory", leaves=["some.file"])
    assert not branch.is_empty


def test_single_directory_w_child_dir() -> None:
    """A single directory with another child directory inside it."""
    branch = Branch("directory", branches=[Branch("subdir")])
    assert not branch.is_empty


def test_nested_structure() -> None:
    """A mix of empty and non-empty branches"""
    parent = Branch("parent")
    first_child = Branch("first", leaves=["some.file", "another.file"])
    second_child = Branch("second", leaves=["some.file"])
    third_child = Branch("third")
    first_child.add_child_branch(second_child)
    parent.add_child_branch(first_child)
    parent.add_child_branch(third_child)
    assert not parent.is_empty
    assert not first_child.is_empty
    assert not second_child.is_empty
    assert third_child.is_empty


def test_tree_is_empty_root() -> None:
    """Test wrapper on tree level: True outcome"""
    tree = Tree(Branch("root"))
    assert tree.is_empty


def test_tree_w_file_at_root_level_not_empty() -> None:
    """Test wrapper on tree level: False outcome"""
    tree = Tree(Branch("root"))
    tree.add_leaf("some.file")
    assert not tree.is_empty


def test_tree_w_directory_at_root_level_not_empty() -> None:
    """Test wrapper on tree level: False outcome"""
    tree = Tree(Branch("root"))
    tree.add_branch(Branch("folder"))
    assert not tree.is_empty
