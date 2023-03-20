import transformers
import json
import time
import hnswlib
import numpy as np

from flask import Flask, request
from flask_cors import CORS

from onnxruntime import InferenceSession

with open('/large_data/texts.json', 'rb') as f:
    texts = json.loads(f.read())

with open('/large_data/embs.npy', 'rb') as f:
    embs = np.load(f)


tokenizer = transformers.AutoTokenizer.from_pretrained("microsoft/deberta-v3-base")
session = InferenceSession("/large_data/model.onnx", providers=['CPUExecutionProvider'])

cossim = lambda emb, embs: np.sum(emb * embs, axis=-1)

app = Flask(__name__)
cors = CORS()
cors.init_app(app)

MAX_LENGTH = 128

hnsw_search = hnswlib.Index(space='l2', dim=embs.shape[-1])
hnsw_search.init_index(max_elements=len(embs), ef_construction=200, M=16)
hnsw_search.add_items(np.array(embs), np.arange(len(embs)))
hnsw_search.set_ef(50)

def preprocess(text):
    x = tokenizer(text, padding='max_length', max_length=MAX_LENGTH, truncation=True, return_tensors='np')
    x = {k:v for k,v in x.items() if k != 'token_type_ids'}
    return x

def search(emb, embs, k=20):
    topk = list(reversed(np.argsort(cossim(emb, embs))[-k:]))
    answers = [texts[idx] for idx in topk]
    return answers

def do_hnsw_search(emb):
    labels, distances = hnsw_search.knn_query(emb, k=20)
    print(labels.shape)
    return [texts[idx] for idx in labels[0]]

def do_better_hnsw_search(emb, k=20):
    labels, distances = hnsw_search.knn_query(emb, k=100)
    indices = labels[0]
    subsample_embs = np.vstack([embs[idx] for idx in indices])
    topk = list(reversed(np.argsort(cossim(emb, subsample_embs))[-k:]))
    return [texts[indices[idx]] for idx in topk]

@app.route("/get_questions/", methods=['GET', 'POST'])
def get_questions():
    st = time.time()
    query = json.loads(request.data)['query']
    
    emb = session.run(["output"], preprocess(query))[0][0]
    time1 = time.time() - st
    # answers = search(emb, embs)
    answers = do_better_hnsw_search(emb)
    time2 = time.time() - st - time1
    
    return json.dumps({'answers': answers, 'time': str(time1) + '\n' + str(time2)})

app.run(port=3333, host='0.0.0.0')