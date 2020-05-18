import json
from io import BytesIO
from pathlib import Path
from tokenize import tokenize

import click

SECTIONS = [
    'md_buttons',
    'md_install',
    'py_install',
    'md_create',
    'py_create',
    'md_script',
    'py_script',
    'md_display',
    'py_display', ]


@click.command()
@click.option(
    '-t',
    '--template-path',
    type=click.Path(exists=True, readable=True),
    required=True,
    help='Path to pydeck Jupyter Notebook template.')
@click.argument('files', nargs=-1)
def main(files, template_path):
    for path in files:
        try:
            convert_file(path, template_path)
        except Exception as e:
            print(f'Failed on file: {path}')
            print(e)


def convert_file(path, template_path):
    """Convert python script to Jupyter Notebook

    Args:
        - path: Path to _Python_ file
        - template_path: Path to Jupyter Notebook template
    """
    path = Path(path)

    with open(path) as f:
        lines = f.readlines()

    ee_script_block = extract_ee_script(lines)
    pydeck_block = convert_pydeck_block(ee_script_block)

    # Load Pydeck notebook template
    with open(template_path) as f:
        template_lines = f.readlines()

    # Find index of line to replace
    replace_ind = [
        ind for ind, x in enumerate(template_lines)
        if 'REPLACE_WITH_CUSTOM_EE_SCRIPT' in x][0]

    # Remove this template line
    template_lines.pop(replace_ind)

    # Insert into list
    # Ref: https://stackoverflow.com/a/3748092
    template_lines[replace_ind:replace_ind] = pydeck_block

    # Create path for notebook in same directory
    out_path = path.parents[0] / (path.stem + '.ipynb')
    with open(out_path, 'w') as f:
        f.writelines(template_lines)


def extract_ee_script(lines):
    """Extract EE script from python file
    """
    # The nth section used for python script
    n_section = [ind for ind, x in enumerate(SECTIONS) if x == 'py_script'][0]

    # Find indices of blocks
    # Each block starts with `# %%`
    blocks_idx = [
        ind for ind, x in enumerate(lines) if x.strip().startswith('# %')]
    assert len(blocks_idx) == len(SECTIONS), 'wrong number of blocks'

    # Find start, end indices of python script block
    start_idx, end_idx = blocks_idx[n_section:n_section + 2]

    return lines[start_idx:end_idx]


def convert_pydeck_block(lines):
    """

    - Remove any `Map.setCenter` commands (todo in future: parse?)
    - Extract `Map.addLayer`, use to create Image object that can be passed to Deck.gl

    """
    out_lines = []

    for line in lines:
        stripped = line.lower().strip()
        if not stripped.startswith('map'):
            out_lines.append(line)
            continue

        if stripped.startswith('map.addlayer'):
            line = handle_add_layer(line)
            out_lines.append(line)
            continue

        if stripped.startswith('map.setcenter'):
            line = handle_set_center(line)
            out_lines.append(line)
            continue

    # stringify to put in JSON
    out_lines = [json.dumps(l) for l in out_lines]

    # Add ,\n to each line
    out_lines = [l + ',\n' for l in out_lines]

    # Remove , from last line
    out_lines[-1] = out_lines[-1][:-2] + '\n'

    return out_lines


def handle_add_layer(line):
    """Convert Map.addLayer to EarthEngineLayer
    """
    # https://geemap.readthedocs.io/en/latest/readme.html#usage
    # Args are: eeObject, visParams, name, shown, opacity
    add_layer_args = tokenize_command(line, 5)
    ee_object, vis_params, _, _, opacity = add_layer_args

    kwargs = []
    if ee_object:
        kwargs.append(f'ee_object={ee_object}')

    if vis_params:
        kwargs.append(f'vis_params={vis_params}')

    if opacity:
        kwargs.append(f'opacity={opacity}')

    return f"ee_layers.append(EarthEngineLayer({', '.join(kwargs)}))\n"


def handle_set_center(line):
    """Convert Map.setCenter to pydeck.ViewState
    """
    # https://geemap.readthedocs.io/en/latest/readme.html#usage
    # Args are: lon, lat, zoom
    set_center_args = tokenize_command(line, 3)
    longitude, latitude, zoom = set_center_args

    kwargs = []
    if longitude:
        kwargs.append(f'longitude={longitude}')

    if latitude:
        kwargs.append(f'latitude={latitude}')

    if zoom:
        kwargs.append(f'zoom={zoom}')

    return f"view_state = pdk.ViewState({', '.join(kwargs)})\n"


def tokenize_command(line, n_args):
    tokens = tokenize_line(line)
    args = [''] * n_args
    args_counter = 0
    depth = 0
    for token in tokens:
        # Haven't entered function yet
        if depth == 0 and not (token.type == 53 and token.string == '('):
            continue

        if token.string in ['(', '{', '[']:
            if depth > 0:
                args[args_counter] += token.string

            depth += 1
            continue

        if token.string in [')', '}', ']']:
            if depth > 1:
                args[args_counter] += token.string

            depth -= 1
            continue

        if depth == 1 and token.string == ',':
            args_counter += 1
            continue

        args[args_counter] += token.string

    return args


def stringify(lines):
    """Wrap lines in double quotes, to allow to be saved in JSON
    """
    return [json.dumps(l) for l in lines]


def tokenize_line(line):
    """

    Ref: https://stackoverflow.com/a/54375074
    """
    file = BytesIO(line.encode())
    return list(tokenize(file.readline))


if __name__ == '__main__':
    main()
