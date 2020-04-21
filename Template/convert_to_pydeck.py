from io import BytesIO
from tokenize import tokenize

# with open('../Visualization/hillshade.py') as f:
#     lines = f.readlines()

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


def extract_ee_script(lines):
    """Extract EE script from python file
    """
    # The nth section used for python script
    nSection = [ind for ind, x in enumerate(SECTIONS) if x == 'py_script'][0]

    # Find indices of blocks
    blocks_idx = [
        ind for ind, x in enumerate(lines) if x.strip().startswith('# %')]
    assert len(blocks_idx) == len(SECTIONS), 'wrong number of blocks'

    # Find start, end indices of python script block
    start_idx, end_idx = blocks_idx[nSection:nSection + 2]

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

    # Right now only deal with a single Map.addLayer
    add_layer = added_layers[0]
    add_layer_params = ['pydeck_eeObject', 'pydeck_visParams']
    for param, value in zip(add_layer_params, add_layer):
        if value:
            out_lines.append(f'{param} = {value}')

    return out_lines


def tokenize_line(line):
    """

    Ref: https://stackoverflow.com/a/54375074
    """
    file = BytesIO(line.encode())
    return list(tokenize(file.readline))


# line = "Map.addLayer(alosChili, alosChiliVis, 'ALOS CHILI')"
