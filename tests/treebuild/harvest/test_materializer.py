"""unit tests for src/treebuild/creation/filesystem.py"""

from pathlib import Path

from pytest import MonkeyPatch

from treebuild.harvest.materializer import Materializer
from treebuild.tree.branches import Branch, Tree


# --- Test roundtrip: Create the files, check they exist, then delete, check they do not exist anymore.  ---
def test_roundtrip_empty_tree(tree: Tree, tmp_path: Path) -> None:
    """Even if the tree is empty, should still create a directory with the given root name."""
    # write files
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path=tmp_path)
    assert (tmp_path / tree.root.name).exists()

    # delete files:
    materializer.dematerialize_tree(tree, base_path=tmp_path)
    assert not (tmp_path / tree.root.name).exists()


def test_roundtrip_tree_only_files_in_root(tree: Tree, tmp_path: Path) -> None:
    """A directory with no subdirectories, just files"""
    # Construct set of expected paths
    filenames = sorted(["file_1.txt", "code.py", "more_code.java", "dataset.xlsx"])
    expected_items = [tmp_path / tree.root.name / Path(fn) for fn in filenames]

    # build tree
    for f in filenames:
        tree.add_leaf(f)

    # write files
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path=tmp_path)
    assert all(item.exists() for item in expected_items)

    # delete files
    materializer.dematerialize_tree(tree, base_path=tmp_path)
    assert not any(item.exists() for item in expected_items)


def test_roundtrip_tree_w_single_subdir_under_root(tree: Tree, tmp_path: Path) -> None:
    """
    Directory structure: ./subdir/file.txt , given there are a couple of files in this sub-directory
    """

    # Construct set of expected paths
    filenames = sorted(["file_1.txt", "code.py", "more_code.java", "dataset.xlsx"])
    expected_items = [
        tmp_path / tree.root.name / "folder" / Path(fn) for fn in filenames
    ]

    # build tree
    folder = Branch("folder")
    for f in filenames:
        folder.add_leaf(f)
    tree.add_branch(folder)

    # write files
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path=tmp_path)
    assert all(item.exists() for item in expected_items)

    # delete files
    materializer.dematerialize_tree(tree, base_path=tmp_path)
    assert not any(item.exists() for item in expected_items)


def test_roundtrip_tree_multiple_subdirs_at_same_level(
    tree: Tree, tmp_path: Path
) -> None:
    """
    Directory structure: ./subdir/file.txt, and ./second_folder/file.txt.
    """
    # Construct set of expected paths
    files_in_first_folder = sorted(
        ["first_file.py", "second_file.css", "third_file.md"]
    )
    files_in_second_folder = sorted(["another_file.txt"])
    expected_items = [
        tmp_path / tree.root.name / "folder1" / Path(fn) for fn in files_in_first_folder
    ]
    expected_items.extend(
        [
            tmp_path / tree.root.name / "folder2" / Path(fn)
            for fn in files_in_second_folder
        ]
    )

    # build tree
    first_folder = Branch("folder1")
    for f in sorted(files_in_first_folder):
        first_folder.add_leaf(f)

    second_folder = Branch("folder2")
    for f in sorted(files_in_second_folder):
        second_folder.add_leaf(f)

    tree.add_branch(first_folder)
    tree.add_branch(second_folder)

    # write files
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path=tmp_path)
    assert all(item.exists() for item in expected_items)

    # delete files
    materializer.dematerialize_tree(tree, base_path=tmp_path)
    assert not any(item.exists() for item in expected_items)


def test_roundtrip_tree_nested_subdirs(tree: Tree, tmp_path: Path) -> None:
    """
    Directory structure: ./subdir/subsubdir/file.txt (a file in a nested directory)
    """
    # Construct set of expected paths
    files_in_second_folder = sorted(
        ["first_file.py", "second_file.css", "third_file.md"]
    )
    expected_items = [
        tmp_path / tree.root.name / "folder1" / "folder2" / Path(fn)
        for fn in files_in_second_folder
    ]

    # build tree
    first_folder = Branch("folder1")
    second_folder = Branch("folder2")
    for f in sorted(files_in_second_folder):
        second_folder.add_leaf(f)

    first_folder.add_child_branch(second_folder)
    tree.add_branch(first_folder)

    # write files
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path=tmp_path)
    assert all(item.exists() for item in expected_items)

    # delete files
    materializer.dematerialize_tree(tree, base_path=tmp_path)
    assert not any(item.exists() for item in expected_items)


def test_roundtrip_tree_mixed_leaves_and_branches(tree: Tree, tmp_path: Path) -> None:
    """
    Directory structure: ./file_in_root.txt, ./subdir/file.py, ./subdir/subsubdir/more_files.py
    """
    # Construct set of expected paths
    files_in_root = sorted(["file_in_root_dir.txt", "another_file_in_root_dir.md"])
    files_in_first_folder = sorted(
        ["first_file.py", "second_file.css", "empty_directory"]
    )
    files_in_second_folder = sorted(
        ["third_file.py", "fourth_file.py", "fifth_file.readme"]
    )
    expected_items = [tmp_path / tree.root.name / Path(fn) for fn in files_in_root]
    expected_items.extend(
        [
            tmp_path / tree.root.name / "first_folder" / Path(fn)
            for fn in files_in_first_folder
        ]
    )
    expected_items.extend(
        [
            tmp_path / tree.root.name / "first_folder" / "second_folder" / Path(fn)
            for fn in files_in_second_folder
        ]
    )
    # build tree
    for f in files_in_root:
        tree.add_leaf(f)

    first_folder = Branch("first_folder")
    for f in files_in_first_folder:
        first_folder.add_leaf(f)

    second_folder = Branch("second_folder")
    for f in sorted(files_in_second_folder):
        second_folder.add_leaf(f)

    first_folder.add_child_branch(second_folder)
    tree.add_branch(first_folder)

    # write files
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path=tmp_path)
    assert all(item.exists() for item in expected_items)

    # delete files
    materializer.dematerialize_tree(tree, base_path=tmp_path)
    assert not any(item.exists() for item in expected_items)


def test_roundtrip_defaults_to_cwd(
    tree: Tree, tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """If no base_path is provided --> should write into cwd. Use MonkeyPatch to overwrite cwd to the tmp_path."""

    # set cwd to the temporary path
    monkeypatch.chdir(tmp_path)

    # test with just an empty root directory
    materializer = Materializer()
    materializer.materialize_tree(tree)
    assert (Path.cwd() / tree.root.name).exists()

    materializer.dematerialize_tree(tree)
    assert not (Path.cwd() / tree.root.name).exists()
