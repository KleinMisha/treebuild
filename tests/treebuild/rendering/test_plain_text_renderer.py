"""Unit tests for src/treebuild/rendering/plain_text_renderer.py"""

from tests.conftest import assert_strings_equal
from treebuild.rendering.plain_text_renderer import PlainTextRenderer
from treebuild.tree.branches import Branch, Tree


def test_render_empty_tree(tree: Tree) -> None:
    """Basic case of just the root directory"""
    renderer = PlainTextRenderer()
    actual = renderer.render_tree(tree, include_root=True)
    assert actual == tree.root.name
    actual = renderer.render_tree(tree)
    assert actual == "."


def test_render_tree_only_files_in_root(tree: Tree) -> None:
    """A directory with no subdirectories, just files"""

    # Manually construct expected result
    filenames = sorted(["file_1.txt", "code.py", "more_code.java", "dataset.xlsx"])

    expected = "\n".join(
        ["."] + [f"├── {file}" for file in filenames[:-1]] + [f"└── {filenames[-1]}"]
    )

    # Use renderer
    for f in filenames:
        tree.add_leaf(f)
    renderer = PlainTextRenderer()
    actual = renderer.render_tree(tree)
    assert_strings_equal(actual, expected)


def test_render_tree_w_single_subdir_under_root(tree: Tree) -> None:
    """
    Directory structure: ./subdir/file.txt , given there are a couple of files in this sub-directory
    """
    # Manually construct the expected outcome
    filenames = sorted(["file_1.txt", "code.py", "more_code.java", "dataset.xlsx"])
    expected = "\n".join(
        ["."]
        + ["└── folder"]
        + [" " * 4 + f"├── {file}" for file in filenames[:-1]]
        + [" " * 4 + f"└── {filenames[-1]}"]
    )

    # Use renderer
    folder = Branch("folder")
    for f in filenames:
        folder.add_leaf(f)
    tree.add_branch(folder)

    renderer = PlainTextRenderer()
    actual = renderer.render_tree(tree)
    assert_strings_equal(actual, expected)


def test_render_tree_multiple_subdirs_at_same_level(tree: Tree) -> None:
    """
    Directory structure: ./subdir/file.txt, and ./second_folder/file.txt.
    """
    # Manually construct the expected outcome
    files_in_first_folder = sorted(
        ["first_file.py", "second_file.css", "third_file.md"]
    )
    files_in_second_folder = sorted(["another_file.txt"])
    expected = "\n".join(
        ["."]
        + ["├── folder1"]
        + ["│   " + f"├── {file}" for file in files_in_first_folder[:-1]]
        + ["│   " + f"└── {files_in_first_folder[-1]}"]
        + ["└── folder2"]
        + [" " * 4 + f"├── {file}" for file in files_in_second_folder[:-1]]
        + [" " * 4 + f"└── {files_in_second_folder[-1]}"]
    )

    # Use renderer
    first_folder = Branch("folder1")
    for f in sorted(files_in_first_folder):
        first_folder.add_leaf(f)

    second_folder = Branch("folder2")
    for f in sorted(files_in_second_folder):
        second_folder.add_leaf(f)

    tree.add_branch(first_folder)
    tree.add_branch(second_folder)
    renderer = PlainTextRenderer()
    actual = renderer.render_tree(tree)
    assert_strings_equal(actual, expected)


def test_render_tree_nested_subdirs(tree: Tree) -> None:
    """
    Directory structure: ./subdir/subsubdir/file.txt (a file in a nested directory)
    """
    # Manually construct the expected outcome
    files_in_second_folder = sorted(
        ["first_file.py", "second_file.css", "third_file.md"]
    )
    expected = "\n".join(
        ["."]
        + ["└── folder1"]
        + [" " * 4 + "└── folder2"]
        + [" " * 4 + " " * 4 + f"├── {file}" for file in files_in_second_folder[:-1]]
        + [" " * 4 + " " * 4 + f"└── {files_in_second_folder[-1]}"]
    )

    # Use renderer
    first_folder = Branch("folder1")
    second_folder = Branch("folder2")
    for f in sorted(files_in_second_folder):
        second_folder.add_leaf(f)

    first_folder.add_child_branch(second_folder)
    tree.add_branch(first_folder)
    renderer = PlainTextRenderer()
    actual = renderer.render_tree(tree)
    assert_strings_equal(actual, expected)


def test_render_tree_mixed_leaves_and_branches(tree: Tree) -> None:
    """
    Directory structure: ./file_in_root.txt, ./subdir/file.py, ./subdir/subsubdir/more_files.py
    """
    # Manually construct the expected outcome
    files_in_root = sorted(["file_in_root_dir.txt", "another_file_in_root_dir.md"])
    files_in_first_folder = sorted(
        ["first_file.py", "second_file.css", "empty_directory"]
    )
    files_in_second_folder = sorted(
        ["third_file.py", "fourth_file.py", "fifth_file.readme"]
    )
    expected = "\n".join(
        ["."]
        + ["├── first_folder"]
        + ["│   " + "├── second_folder"]
        + ["│   " + "│   " + f"├── {file}" for file in files_in_second_folder[:-1]]
        + ["│   " + "│   " + f"└── {files_in_second_folder[-1]}"]
        + ["│   " + f"├── {file}" for file in files_in_first_folder[:-1]]
        + ["│   " + f"└── {files_in_first_folder[-1]}"]
        + [f"├── {file}" for file in files_in_root[:-1]]
        + [f"└── {files_in_root[-1]}"]
    )

    # use renderer
    for f in files_in_root:
        tree.add_leaf(f)

    first_folder = Branch("first_folder")
    for f in files_in_first_folder:
        first_folder.add_leaf(f)

    second_folder = Branch("second_folder")
    for f in files_in_second_folder:
        second_folder.add_leaf(f)

    first_folder.add_child_branch(second_folder)
    tree.add_branch(first_folder)
    renderer = PlainTextRenderer()
    actual = renderer.render_tree(tree)
    assert_strings_equal(actual, expected)
