"""Build static HTML site from directory of HTML templates and plain files."""

import pathlib
import json
import shutil
import sys

import click
import jinja2


@click.command()
@click.option('-o', '--output', type=click.Path(), help='Output directory.')
# Not sure whether line 7 is correct or not?
@click.option('-v', '--verbose', is_flag=True, default=False,
              help='Print more output.')
@click.argument("input_dir", nargs=1, type=click.Path(exists=True))
def main(output, verbose, input_dir):
    """Templated static website generator."""
    input_dir = pathlib.Path(input_dir)

    if not output:
        # by default, render templates to INPUT_DIR/html
        output_dir = input_dir/'html'
    else:
        output_dir = pathlib.Path(output)

    # Error checking
    if not input_dir.exists():
        print('Error: ', str(input_dir), 'is not a directory')
        sys.exit(1)  # exit if input directory not exists
    if output_dir.exists():
        print('Error: ', str(output_dir), 'already exists')
        sys.exit(1)  # exit if output directory already exists

    output_dir.mkdir()  # create the output directory

    # 1. Read configuration file
    config_dir = input_dir/'config.json'
    with config_dir.open() as config_file:
        config_data = json.load(config_file)

    template_dir = input_dir/'templates'
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
    )

    # 3. Copy static/ directory
    static_dir = input_dir/'static/'
    if static_dir.exists():
        shutil.copytree(static_dir, output_dir, dirs_exist_ok=True)

        if verbose:  # verbose mode
            print('Copied', static_dir, '->', output_dir)

    # 2. Render templates
    for config in config_data:
        conf(config, template_env, output_dir, verbose)

    # handle config function(c, env, output_dir line 39)

    # Serveral other weird questions:
    # How to deal with default directory?
    # If the input directory does not exist,
    #   will it automatically exit with an error message?


def conf(config, env, output_dir, verbose):
    """Loop for each config object."""
    url = config['url'].lstrip("/")

    template = env.get_template(config['template'])  # don't know?
    out = template.render(config['context'])

    url_dir = output_dir/url
    url_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir/url/"index.html"
    output_path.touch()

    # Write output
    with output_path.open('w'):
        output_path.write_text(out)

    if verbose:  # verbose mode
        print('Rendered', config['template'], '->', output_path)


if __name__ == "__main__":
    main()
