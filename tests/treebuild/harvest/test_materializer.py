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

    # build tree
    filenames = sorted(["file_1.txt", "code.py", "more_code.java", "dataset.xlsx"])
    for f in filenames:
        tree.add_leaf(f)

    # write files
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path=tmp_path)
    assert all((tmp_path / path).exists() for path in tree.paths)

    # delete files
    materializer.dematerialize_tree(tree, base_path=tmp_path)
    assert not any((tmp_path / path).exists() for path in tree.paths)


def test_roundtrip_tree_w_single_subdir_under_root(tree: Tree, tmp_path: Path) -> None:
    """
    Directory structure: ./subdir/file.txt , given there are a couple of files in this sub-directory
    """

    # build tree
    filenames = sorted(["file_1.txt", "code.py", "more_code.java", "dataset.xlsx"])

    folder = Branch("folder")
    for f in filenames:
        folder.add_leaf(f)
    tree.add_branch(folder)

    # write files
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path=tmp_path)
    assert all((tmp_path / path).exists() for path in tree.paths)

    # delete files
    materializer.dematerialize_tree(tree, base_path=tmp_path)
    assert not any((tmp_path / path).exists() for path in tree.paths)


def test_roundtrip_tree_multiple_subdirs_at_same_level(
    tree: Tree, tmp_path: Path
) -> None:
    """
    Directory structure: ./subdir/file.txt, and ./second_folder/file.txt.
    """

    # build tree
    files_in_first_folder = sorted(
        ["first_file.py", "second_file.css", "third_file.md"]
    )
    files_in_second_folder = sorted(["another_file.txt"])

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
    assert all((tmp_path / path).exists() for path in tree.paths)

    # delete files
    materializer.dematerialize_tree(tree, base_path=tmp_path)
    assert not any((tmp_path / path).exists() for path in tree.paths)


def test_roundtrip_tree_nested_subdirs(tree: Tree, tmp_path: Path) -> None:
    """
    Directory structure: ./subdir/subsubdir/file.txt (a file in a nested directory)
    """

    # build tree
    files_in_second_folder = sorted(
        ["first_file.py", "second_file.css", "third_file.md"]
    )

    first_folder = Branch("folder1")
    second_folder = Branch("folder2")
    for f in sorted(files_in_second_folder):
        second_folder.add_leaf(f)

    first_folder.add_child_branch(second_folder)
    tree.add_branch(first_folder)

    # write files
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path=tmp_path)
    assert all((tmp_path / path).exists() for path in tree.paths)

    # delete files
    materializer.dematerialize_tree(tree, base_path=tmp_path)
    assert not any((tmp_path / path).exists() for path in tree.paths)


def test_roundtrip_tree_mixed_leaves_and_branches(tree: Tree, tmp_path: Path) -> None:
    """
    Directory structure: ./file_in_root.txt, ./subdir/file.py, ./subdir/subsubdir/more_files.py
    """

    # build tree
    files_in_root = sorted(["file_in_root_dir.txt", "another_file_in_root_dir.md"])
    files_in_first_folder = sorted(
        ["first_file.py", "second_file.css", "empty_directory"]
    )
    files_in_second_folder = sorted(
        ["third_file.py", "fourth_file.py", "fifth_file.readme"]
    )

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
    assert all((tmp_path / path).exists() for path in tree.paths)

    # delete files
    materializer.dematerialize_tree(tree, base_path=tmp_path)
    assert not any((tmp_path / path).exists() for path in tree.paths)


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


# --- Test adding .gitkeep, to empty directories ---
def test_add_gitkeep_to_root(tree: Tree, tmp_path: Path) -> None:
    """An empty tree, should now contain a `.gitkeep` file after materializing"""
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path=tmp_path, gitkeep=True)
    assert (tmp_path / tree.root.name).exists()
    assert (tmp_path / tree.root.name / ".gitkeep").exists()


def test_gitkeep_only_added_if_root_empty(tree: Tree, tmp_path: Path) -> None:
    """No `.gitkeep` file should be added if the directory isn't empty."""
    tree.add_leaf("some.file")
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path=tmp_path, gitkeep=True)
    assert (tmp_path / tree.root.name).exists()
    assert not (tmp_path / tree.root.name / ".gitkeep").exists()


def test_add_gitkeep_empty_child_branch(tree: Tree, tmp_path: Path) -> None:
    """Adding a `.gitkeep` file (no contents) into an empty child directory."""
    # build tree
    folder = Branch("folder")
    tree.add_branch(folder)

    # write files
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path=tmp_path, gitkeep=True)
    assert all((tmp_path / path).exists() for path in tree.paths)
    assert (tmp_path / tree.root.name / folder.name / ".gitkeep").exists()


def test_gitkeep_only_added_if_child_branch_empty(tree: Tree, tmp_path: Path) -> None:
    """No `.gitkeep` file should be added if the directory isn't empty."""
    # build tree
    filenames = sorted(["file_1.txt", "code.py", "more_code.java", "dataset.xlsx"])

    folder = Branch("folder")
    for f in filenames:
        folder.add_leaf(f)
    tree.add_branch(folder)

    # write files
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path=tmp_path, gitkeep=True)
    assert all((tmp_path / path).exists() for path in tree.paths)
    assert not (tmp_path / tree.root.name / folder.name / ".gitkeep").exists()


def test_add_gitkeep_nested_subdir(tree: Tree, tmp_path: Path) -> None:
    """Make sure gitkeep parameter is carried over through recursion correctly."""
    # build tree
    first_folder = Branch("first")
    second_folder = Branch("second")
    first_folder.add_child_branch(second_folder)
    tree.add_branch(first_folder)

    # write files
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path=tmp_path, gitkeep=True)
    assert all((tmp_path / path).exists() for path in tree.paths)
    assert not (tmp_path / tree.root.name / first_folder.name / ".gitkeep").exists()
    assert (
        tmp_path / tree.root.name / first_folder.name / second_folder.name / ".gitkeep"
    ).exists()


def test_no_gitkeep_if_set_to_false(tree: Tree, tmp_path: Path) -> None:
    """Even if directory is empty, no `gitkeep` should be added if parameter is set to FALSE."""
    # build tree
    folder = Branch("folder")
    tree.add_branch(folder)

    # write files
    materializer = Materializer()
    materializer.materialize_tree(tree, base_path=tmp_path, gitkeep=False)
    assert all((tmp_path / path).exists() for path in tree.paths)
    assert not (tmp_path / tree.root.name / folder.name / ".gitkeep").exists()
