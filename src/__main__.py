import boilerutils
import builder
import sys
import os
import click
import shutil
from coloring import Color, colorize

@click.group()
@click.option("-t", "--test", is_flag=True, default=False, help="sets test directories for dependencies and config")
def main(test):
    # test mode
    if test:
        boilerutils.TEST = True
    boilerutils.update()

@main.command()
@click.option("-f", "--formula", is_flag=True, default=False)
def list(formula):
    files: list
    if formula:
        files = [i.replace(".json", "") for i in os.listdir(boilerutils.FORMULA_DIR)]
    else:
        files = [i.replace(".json", "") for i in os.listdir(boilerutils.TARGET_DIR)]
    for i in files:
            print(colorize(i, Color.CYAN))


@main.command()
@click.argument("target", nargs=1)
@click.option("-p", "--prefix", default="environment", prompt=True, show_default=True, help="install prefix")
@click.option("-nr", "--no-run", is_flag=True, default=False, help="don't run the build script once created")
@click.option("-ud", "--use-downloads", is_flag=True, default=False, help="use existing download when possible")
@click.option("-kd", "--keep-downloads", is_flag=True, default=False, help="don't remove downloaded archive")
@click.option("-nce", "--no-check-exists", is_flag=True, default=False, help="don't check if executable exists within prefix when executing the build script")
def install(target, prefix, no_run, use_downloads, keep_downloads, no_check_exists):
    """ TARGET: run list command for list of available targets """
    
    # assign prefix
    if os.path.isabs(prefix):
         boilerutils.PREFIX = prefix
    else:
         boilerutils.PREFIX = os.path.join(boilerutils.CWD, prefix)
    
    # validate target
    if any(i.replace(".json", "") == target for i in os.listdir(boilerutils.TARGET_DIR)) is False:
         print(colorize("invalid target", Color.RED))
         return

    # create builder
    target_builder = builder.Builder(target)
    target_builder.load_build()
    target_builder.download_source(use_downloads, keep_downloads)
    target_builder.create_build_script(not no_check_exists)

    # running the script
    if no_run:
        print(colorize("skipping run ...", Color.YELLOW))
    else:   
        target_builder.run_build_script()

    print(colorize("process complete !", Color.GREEN))


@main.command()
def clean():
    "clean the cache directory"
    for i in os.listdir(boilerutils.TMP_DIR):
        print(colorize("removing "+i, Color.CYAN))
        shutil.rmtree(os.path.join(boilerutils.TMP_DIR, i))
    print(colorize("process complete !", Color.GREEN))

if __name__ == "__main__":
    main()
