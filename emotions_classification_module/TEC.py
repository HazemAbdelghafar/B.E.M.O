from tokenizers import Tokenizer
import onnxruntime as ort
import numpy as np
from os import cpu_count
import sys
import json

em_lbls = [
    'admiration', 'amusement', 'anger', 'annoyance', 'approval', 'caring', 
    'confusion', 'curiosity', 'desire', 'disappointment', 'disapproval', 
    'disgust', 'embarrassment', 'excitement', 'fear', 'gratitude', 'grief', 
    'joy', 'love', 'nervousness', 'optimism', 'pride', 'realization', 
    'relief', 'remorse', 'sadness', 'surprise', 'neutral'
]

tok_path = "./roberta-base-go_emotions/tokenizer.json"
mdl_path = "./model/roberta_go_emotions_quantized.onnx"

tok = Tokenizer.from_file(tok_path)
pad_id = tok.token_to_id("[PAD]")
if pad_id is None:
    tok.add_special_tokens(["[PAD]"])
    pad_id = tok.token_to_id("[PAD]")

tok.enable_padding(pad_id=pad_id)

if len(sys.argv) > 1:
    smpl_sntncs = [sys.argv[1]]
else:
    print("No text input provided")
    sys.exit()

enc_tkns = tok.encode_batch(smpl_sntncs)

def ld_mdl(mdl_pth):
    opts = ort.SessionOptions()
    opts.inter_op_num_threads = cpu_count()
    opts.intra_op_num_threads = cpu_count()
    provs = ["CPUExecutionProvider"]
    return ort.InferenceSession(mdl_pth, sess_options=opts, providers=provs)

mdl = ld_mdl(mdl_path)
out_name = mdl.get_outputs()[0].name

inpt_fd = {
    "input_ids": [tkn.ids for tkn in enc_tkns],
    "attention_mask": [tkn.attention_mask for tkn in enc_tkns]
}

lgts = mdl.run([out_name], inpt_fd)[0]

def sgmd(x):
    return 1/(1+np.exp(-x))

probs = sgmd(lgts)

top_2_indices = np.argsort(probs, axis=1)[:, -2:]
top_2_labels = [[em_lbls[idx] for idx in indices] for indices in top_2_indices]
top_2_probs = np.sort(probs, axis=1)[:, -2:]

results = []
for i, sentence in enumerate(smpl_sntncs):
    result = {
        "sentence": sentence,
        "top_label": top_2_labels[i][-1],
        "top_label_prob": float(top_2_probs[i][-1]),
        "second_top_label": top_2_labels[i][-2] if top_2_probs[i][0] >= 0.3 else "nth",
        "second_top_label_prob": float(top_2_probs[i][-2])
    }
    results.append(result)

with open("Emotions.json", "w") as f:
    json.dump(results, f, indent=4)
    
    # To run this code, save it in a file named `TEC.py` and execute it from the command line with a text input.
    # For example:
    # python ./TEC.py "I am very happy today!"
    # The output will be saved in a file named `Emotions.json` in the current directory.
