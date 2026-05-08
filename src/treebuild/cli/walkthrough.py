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


def prompt_command(correct_command: str, on_success: CliCommand) -> None:
    """Prompt user to type the required command to proceed with the demo."""
    while True:
        user_input = prompt(">")
        if user_input == correct_command:
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
    echo(
        "Use `treebuild plant` to create a new file to store you're tree's paths into."
    )
    prompt_command(correct_command="treebuild plant", on_success=plant_impl)

    # 3. Set name of root directory / give it a name
    echo(
        "Now let's  name of the root directory 'demo-project' by calling `treebuild seed demo-project`"
    )
    prompt_command(
        correct_command="treebuild seed demo-project",
        on_success=partial(seed_impl, root_name="demo-project", force=False),
    )

    # 4. Check your progress
    echo("You can check the status of your tree using the `treebuild status` command.")
    prompt_command(correct_command="treebuild status", on_success=status_impl)

    # 5. Add a file
    echo(
        "We can now use the `grow` and `prune` commands to add/remove files and directories to this project's tree."
    )
    echo(
        "Add a file called `main.py` in the root directory by calling `treebuild grow main.py`"
    )
    prompt_command(
        correct_command="treebuild grow main.py",
        on_success=partial(grow_impl, paths=["main.py"]),
    )

    # 6. Try adding the same file, but include root-dir as prefix --> Duplicates are skipped automatically
    echo(
        "Let's see what happens if you add the same file again, this time explicitly stating the root as prefix"
    )
    echo("Use `treebuild grow demo-project/main.py`")
    prompt_command(
        correct_command="treebuild grow demo-project/main.py",
        on_success=partial(grow_impl, paths=["demo-project/main.py"]),
    )
    echo(
        "Would you look at that! Treebuild understands you've already added this file and will simply skip it, so you don't need to worry about accidentally adding the same file twice."
    )

    # 7. Add an (empty) directory (NOTE the trailing slash)
    echo(
        "Add an empty directory using `treebuild grow empty-dummy-dir/`."
        "Note the trailing slash in the entered path (signaling a directory)."
    )
    prompt_command(
        correct_command="treebuild grow empty-dummy-dir/",
        on_success=partial(grow_impl, paths=["empty-dummy-dir/"]),
    )

    # 8. Check your progress
    echo("Time to double-check our progress: `treebuild status`")
    prompt_command(correct_command="treebuild status", on_success=status_impl)

    # 9. Add a bunch of additional files / directories (NOTE if parent dir is not empty, you can simple add the full path in one go)
    paths_to_add = [
        "README.md",
        ".dotfile",
        "settings.yml",
        "src/orders.py",
        "src/users.py",
        "src/scripts/cleanup.sh",
        "tests/",
    ]
    echo(
        "We can actually add multiple items in a single call, let's do such to make this project a bit more interesting. "
    )
    echo(f"Call `treebuild grow {paths_to_add}`")
    prompt_command(
        correct_command=f"treebuild grow {paths_to_add}",
        on_success=partial(grow_impl, paths=paths_to_add),
    )
    echo("All paths are interpreted as being relative to the root's directory. ")
    echo(
        "Also note how files placed in nested directories can be added directly by supplying the full path."
    )

    # 10. Check your progress
    echo("Check your progress: `treebuild status`")
    prompt_command(correct_command="treebuild status", on_success=status_impl)

    # 11. Remove a path we actually do not want
    echo(
        "Oops! We still seem to have the dummy directory, remove it by calling `treebuild prune empty-dummy-dir/`"
    )
    prompt_command(
        correct_command="treebuild prune empty-dummy-dir/",
        on_success=partial(prune_impl, paths=["empty-dummy-dir/"]),
    )

    # 12. Check your progress
    echo("Check your progress: `treebuild status`")
    prompt_command(correct_command="treebuild status", on_success=status_impl)

    # 13. Render your tree (using default renderer)
    echo("This looks good. We can now 'harvest' what we've grown. ")
    echo(
        "Let's start by rendering a tree structure by calling `treebuild harvest text`"
    )
    prompt_command(correct_command="treebuild harvest text", on_success=show_rendering)
    echo(
        "We used a vanilla plain text rendering here, "
        "You're encouraged to checkout `treebuild harvest text --help` to checkout the other options for the `--rendering` flag. "
    )
    # 13. Materialize the tree
    echo(
        "That looks good! Let's immediately materialize this project to the filesystem by calling `treebuild harvest scaffold --gitkeep`"
    )
    prompt_command(
        correct_command="treebuild harvest scaffold --gitkeep",
        on_success=partial(scaffold_impl, gitkeep=True),
    )
    echo(
        "The `--gitkeep` flag has added a `.gitkeep` file into any empty directory detected, such that it can be committed to a (remote) repository."
    )

    # 14. You can inspect the tree at "show path", when ready .. we will remove the created files
    pause(
        "Ain't that cool? The project has been al setup. "
        "Check it out, and press any key to proceed into the cleanup procedure (will reset your state to before the demo.)"
    )

    # 15. Cleanup
    echo("Remove the files and directories created: `treebuild harvest teardown`")
    prompt_command(
        correct_command="treebuild harvest teardown", on_success=teardown_impl
    )

    echo("Remove the file storing your paths: `treebuild chop`")
    prompt_command(correct_command="treebuild chop", on_success=chop_impl)

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
