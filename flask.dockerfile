FROM python:3.10
RUN pip install onnxruntime \
    sentencepiece \
    protobuf==3.20.2 \
    transformers \
    hnswlib \
    numpy \
    flask \
    Flask-Cors 
COPY server /server
WORKDIR /server
CMD python app.py
