from dataless.dNN import dNN

config = {
    'prob_type': 'mdds',
    'out_filename': 'save_dir',
    'use_random': True,
    'nodes': 10,
    'edge_prob': 0.75
}

dnn = dNN(**config)
dnn.ping()

