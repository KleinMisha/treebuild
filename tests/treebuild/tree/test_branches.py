"""Unit tests for src/treebuilder/tree/branches.py"""

from treebuild.tree.branches import Branch


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
