import json
from io import BytesIO
from pathlib import Path
from tokenize import tokenize

SECTIONS = [
    'md_buttons',
    'md_install',
    'py_install',
    'md_create',
    'py_create',
    'md_script',
    'py_script',
    'md_display',
    'py_display']

def main(path, template_path):
    path = '../Visualization/hillshade.py'
    path = Path(path)

    with open(path) as f:
        lines = f.readlines()

    ee_script_block = extract_ee_script(lines)
    pydeck_block = set_result_as_pydeck_object(ee_script_block)

    # stringify to put in JSON
    pydeck_block = [json.dumps(l) for l in pydeck_block]

    # Add ,\n to each line
    pydeck_block = [l + ',\n' for l in pydeck_block]

    # Remove , from last line
    pydeck_block[-1] = pydeck_block[-1][:-2] + '\n'

    # Load Pydeck notebook template
    with open(template_path) as f:
        template_lines = f.readlines()

    # Find index of line to replace
    replace_ind = [ind for ind, x in enumerate(template_lines) if 'REPLACE_WITH_CUSTOM_EE_SCRIPT' in x][0]

    # Remove this template line
    template_lines.pop(replace_ind)

    # Insert into list
    # Ref: https://stackoverflow.com/a/3748092
    insert_lines = ['"source": [\n', *pydeck_block, ']\n']
    template_lines[replace_ind:replace_ind] = insert_lines

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
    blocks_idx = [
        ind for ind, x in enumerate(lines) if x.strip().startswith('# %')]
    assert len(blocks_idx) == len(SECTIONS), 'wrong number of blocks'

    # Find start, end indices of python script block
    start_idx, end_idx = blocks_idx[n_section:n_section + 2]

    return lines[start_idx:end_idx]


def set_result_as_pydeck_object(lines):
    """

    - Remove any `Map.setCenter` commands (todo in future: parse?)
    - Extract `Map.addLayer`, use to create Image object that can be passed to Deck.gl

    """
    out_lines = []
    added_layers = []

    for line in lines:
        if not line.lower().strip().startswith('map'):
            out_lines.append(line)
            continue

        tokens = tokenize_line(line)

        # https://developers.google.com/earth-engine/api_docs#mapaddlayer
        # Args are: eeObject, visParams, name, shown, opacity
        add_layer_args = ['', '', '', '', '']
        add_layer_args_counter = 0
        depth = 0
        for token in tokens:
            # Haven't entered function yet
            if depth == 0 and not (token.type == 53 and token.string == '('):
                continue

            if token.string == '(':
                if depth > 0:
                    add_layer_args[add_layer_args_counter] += token.string

                depth += 1
                continue

            if token.string == ')':
                if depth > 1:
                    add_layer_args[add_layer_args_counter] += token.string

                depth -= 1
                continue

            if depth == 1 and token.string == ',':
                add_layer_args_counter += 1
                continue

            add_layer_args[add_layer_args_counter] += token.string

        added_layers.append(add_layer_args)

    # For each Map.addLayer, convert that into an EarthEngineLayer
    for add_layer in added_layers:
        ee_object, vis_params, _, _, opacity = add_layer
        s = 'ee_layers.append(EarthEngineLayer('
        if ee_object:
            s += ee_object

        if vis_params:
            s += ', ' + vis_params

        if opacity:
            s += ', ' + f'opacity={opacity}'

        s += '))\n'
        out_lines.append(s)

    return out_lines


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
