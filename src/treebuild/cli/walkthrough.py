"""implementation of interactive demo and quickstart."""

from functools import partial
from typing import Callable

from typer import confirm, echo, pause, prompt

from treebuild.cli.commands.harvest import render_txt_impl, scaffold_impl, teardown_impl
from treebuild.cli.commands.treebuild import (
    chop_impl,
    grow_impl,
    plant_impl,
    prune_impl,
    seed_impl,
    status_impl,
)
from treebuild.cli.helpers import load_message
from treebuild.core.exceptions import (
    EmptySessionError,
    NoRootSetError,
    RootDirNotFoundError,
)

# A CLI command (implementation) is a function with a zero return.
CliCommand = Callable[[], None]

# Define the expected inputs for the interactive demo. Makes it adjustable / testable (tests can input the 'public' constant)

_PAUSE = "PAUSE"  # sentinel value for typer.pause() input
_PLANT_CMD = "treebuild plant"
_SEED_CMD = "treebuild seed demo-project"
_STATUS_CMD = "treebuild status"
_ADD_FILE_CMD = "treebuild grow main.py"
_ADD_SAME_FILE_CMD = "treebuild grow demo-project/main.py"
_ADD_EMPTY_DIR_CMD = "treebuild grow empty-dummy-dir/"
_DEMO_PATHS = [
    "README.md",
    ".dotfile",
    "settings.yml",
    "src/orders.py",
    "src/users.py",
    "src/scripts/cleanup.sh",
    "tests/",
]
_GROW_MULTIPLE_CMD = f"treebuild grow {' '.join(_DEMO_PATHS)}"
_REMOVE_EMPTY_DIR_CMD = "treebuild prune empty-dummy-dir/"
_RENDER_TO_TEXT_CMD = "treebuild harvest text"
_MATERIALIZE_TO_FILESYSTEM_CMD = "treebuild harvest scaffold --gitkeep"
_DEMATERIALIZE_FROM_FILESYSTEM_CMD = "treebuild harvest teardown"
_CHOP_CMD = "treebuild chop"
CORRECT_DEMO_INPUTS = [
    _PAUSE,  # step 1 (press any key to start)
    _PLANT_CMD,  # step 2
    _SEED_CMD,  # step 3
    _STATUS_CMD,  # step 4
    _ADD_FILE_CMD,  # step 5
    _ADD_SAME_FILE_CMD,  # step 6
    _PAUSE,  # pause for info on adding duplicates
    _ADD_EMPTY_DIR_CMD,  # step 7
    _STATUS_CMD,  # step 8,
    _GROW_MULTIPLE_CMD,  # step 9
    _PAUSE,  # pause
    _STATUS_CMD,  # step 10
    _REMOVE_EMPTY_DIR_CMD,  # step 11
    _STATUS_CMD,  # step 12
    _RENDER_TO_TEXT_CMD,  # step 13
    _MATERIALIZE_TO_FILESYSTEM_CMD,  # step 14
    _PAUSE,  # pause after creation
    _PAUSE,  # pause before entering cleanup (step 15)
    _DEMATERIALIZE_FROM_FILESYSTEM_CMD,  # step 15 a
    _CHOP_CMD,  # step 15 b
]


def prompt_command(correct_command: str, on_success: CliCommand) -> None:
    """Prompt user to type the required command to proceed with the demo."""
    while True:
        user_input = prompt(">")
        if user_input.strip() == correct_command:
            on_success()
            break
        else:
            echo(
                "Not quite there! Make sure to enter the correct command: "
                f" {correct_command}"
            )


def show_rendering() -> None:
    """Wrapper around rendering to have a CliCommand"""
    rendering = render_txt_impl(show_root=True)
    echo(rendering)


def interactive_demo() -> None:
    """Happy path for interactive demo."""

    # 1. Show welcome message
    introduction = load_message("demo_intro.md")
    echo(introduction)
    pause("Press any key to start...")

    # 2. Plant a new tree
    echo("Let's plant a new tree!")
    echo("\n" + "-" * 40)
    echo(f"Use `{_PLANT_CMD}` to create a new file to store you're tree's paths into.")
    prompt_command(correct_command=_PLANT_CMD, on_success=plant_impl)

    # 3. Set name of root directory / give it a name
    echo(
        f"Now let's  name of the root directory 'demo-project' by calling `{_SEED_CMD}`"
    )
    prompt_command(
        correct_command=_SEED_CMD,
        on_success=partial(seed_impl, root_name="demo-project", force=False),
    )

    # 4. Check your progress
    echo(f"You can check the status of your tree using the `{_STATUS_CMD}` command.")
    prompt_command(correct_command=_STATUS_CMD, on_success=status_impl)

    # 5. Add a file
    echo(
        "We can now use the `grow` and `prune` commands to add/remove files and directories to this project's tree.\n "
        f"Add a file called `main.py` in the root directory by calling `{_ADD_FILE_CMD}`"
    )
    prompt_command(
        correct_command=_ADD_FILE_CMD,
        on_success=partial(grow_impl, paths=["main.py"]),
    )

    # 6. Try adding the same file, but include root-dir as prefix --> Duplicates are skipped automatically
    echo(
        "Let's see what happens if you add the same file again, this time explicitly stating the root as prefix\n"
        f"Use `{_ADD_SAME_FILE_CMD}`"
    )
    prompt_command(
        correct_command=_ADD_SAME_FILE_CMD,
        on_success=partial(grow_impl, paths=["demo-project/main.py"]),
    )
    pause(
        "Would you look at that! Treebuild understands you've already added this file and will simply skip it, so you don't need to worry about accidentally adding the same file twice."
    )

    # 7. Add an (empty) directory (NOTE the trailing slash)
    echo(
        f"Add an empty directory using `{_ADD_EMPTY_DIR_CMD}`."
        "Note the trailing slash in the entered path (signaling a directory)."
    )
    prompt_command(
        correct_command=_ADD_EMPTY_DIR_CMD,
        on_success=partial(grow_impl, paths=["empty-dummy-dir/"]),
    )

    # 8. Check your progress
    echo(f"Time to double-check our progress: {_STATUS_CMD}")
    prompt_command(correct_command=_STATUS_CMD, on_success=status_impl)

    # 9. Add a bunch of additional files / directories (NOTE if parent dir is not empty, you can simple add the full path in one go)

    echo(
        "We can actually add multiple items in a single call, let's do such to make this project a bit more interesting. "
    )
    echo(f"Call `{_GROW_MULTIPLE_CMD}`")
    prompt_command(
        correct_command=_GROW_MULTIPLE_CMD,
        on_success=partial(grow_impl, paths=_DEMO_PATHS),
    )
    pause(
        "All paths are interpreted as being relative to the root's directory."
        "Also note how files placed in nested directories can be added directly by supplying the full path."
    )

    # 10. Check your progress
    echo(f"Check your progress: `{_STATUS_CMD}`")
    prompt_command(correct_command=_STATUS_CMD, on_success=status_impl)

    # 11. Remove a path we actually do not want
    echo(
        f"Oops! We still seem to have the dummy directory, remove it by calling `{_REMOVE_EMPTY_DIR_CMD}`"
    )
    prompt_command(
        correct_command=_REMOVE_EMPTY_DIR_CMD,
        on_success=partial(prune_impl, paths=["empty-dummy-dir/"]),
    )

    # 12. Check your progress
    echo(f"Check your progress: `{_STATUS_CMD}`")
    prompt_command(correct_command=_STATUS_CMD, on_success=status_impl)

    # 13. Render your tree (using default renderer)
    echo("This looks good. We can now 'harvest' what we've grown. ")
    echo(
        f"Let's start by rendering a tree structure by calling `{_RENDER_TO_TEXT_CMD}`"
    )
    prompt_command(correct_command=_RENDER_TO_TEXT_CMD, on_success=show_rendering)
    pause(
        "We used a vanilla plain text rendering here, "
        "You're encouraged to checkout `treebuild harvest text --help` to checkout the other options for the `--rendering` flag. "
    )
    # 13. Materialize the tree
    echo(
        f"That looks good! Let's immediately materialize this project to the filesystem by calling `{_MATERIALIZE_TO_FILESYSTEM_CMD}`"
    )
    prompt_command(
        correct_command=_MATERIALIZE_TO_FILESYSTEM_CMD,
        on_success=partial(scaffold_impl, gitkeep=True),
    )
    pause(
        "The `--gitkeep` flag has added a `.gitkeep` file into any empty directory detected, such that it can be committed to a (remote) repository."
    )
    pause(
        "Ain't that cool? The project has been al setup. "
        "Check it out, and press any key to proceed into the cleanup procedure (will reset your state to before the demo.)"
    )

    # 14. Cleanup
    echo(
        f"Remove the files and directories created: `{_DEMATERIALIZE_FROM_FILESYSTEM_CMD}`"
    )
    prompt_command(
        correct_command=_DEMATERIALIZE_FROM_FILESYSTEM_CMD, on_success=teardown_impl
    )

    echo(f"Remove the file storing your paths: `{_CHOP_CMD}`")
    prompt_command(correct_command=_CHOP_CMD, on_success=chop_impl)

    # 15. Done with the demo ---> Enter quickstart guide?
    enter_quickstart = confirm(
        "Congrats you've completed the demo. Proceed with the quickstart setup?"
    )
    if enter_quickstart:
        quickstart_impl()


def interrupt_demo() -> None:
    """If the user quits the demo midway"""
    echo("Demo interrupted. Cleaning up files created in demo.")
    try:
        echo("Removing the created demo project from filesystem.")
        teardown_impl()
    except (NoRootSetError, RootDirNotFoundError):
        echo("No files materialized, no cleanup needed. ")

    try:
        echo("Removing the created session store.")
        chop_impl()
    except EmptySessionError:
        echo("Nothing to cleanup.")
        return


def quickstart_impl() -> None:
    """Allow the user to create, amend, render, and materialize a tree without knowing any of the commands."""
