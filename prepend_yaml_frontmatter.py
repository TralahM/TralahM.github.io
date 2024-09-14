#!/usr/bin/env python

# import re
# import sys
# import yaml
import os

"""
QUARTO_PROJECT_RENDER_ALL	Set to “1” if this is a render of all files in the
project (as opposed to an incremental render or a render for preview).
This unset if Quarto is not rendering all files.

QUARTO_PROJECT_OUTPUT_DIR	Output directory

QUARTO_PROJECT_INPUT_FILES	Newline separated list of all input files being
rendered (passed only to pre-render)

QUARTO_PROJECT_OUTPUT_FILES	Newline separated list of all output files
rendered (passed only to post-render).
"""
quarto_project_render_all = bool(os.getenv("QUARTO_PROJECT_RENDER_ALL"))
quarto_project_output_dir = os.getenv("QUARTO_PROJECT_OUTPUT_DIR")
quarto_project_input_files_arg = os.getenv("QUARTO_PROJECT_INPUT_FILES", None)
quarto_project_output_files_arg = os.getenv(
    "QUARTO_PROJECT_OUTPUT_FILES", None)
quarto_project_input_files = (
    quarto_project_input_files_arg.split(
        "\n") if quarto_project_input_files_arg else []
)
quarto_project_output_files = (
    quarto_project_output_files_arg.split("\n")
    if quarto_project_output_files_arg
    else []
)

example_front_matter = dict(
    title="",
    subtitle="",
    categories="",
    excerpt="",
    header=dict(
        teaser="",
        overlay_color="",
        overlay_image="",
        image="",
        video=dict(id="", provider=""),
    ),
    toc_sticky=True,
    mathjax=True,
    layout="single",
    permalink="/portfolio",
    date="",
)


def main():
    print("Quarto project render all: " + str(quarto_project_render_all))
    print("Quarto project output dir: " + str(quarto_project_output_dir))
    print(
        "Quarto project input files: " +
        str("\n".join(quarto_project_input_files)),
    )
    print(
        "Quarto project output files: " +
        str("\n".join(quarto_project_output_files)),
    )


if __name__ == "__main__":
    main()
