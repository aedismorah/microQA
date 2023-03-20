IP="93.175.9.182"
mkdir large_data
wget http://$IP:5555/download/texts.json --directory-prefix=large_data
wget http://$IP:5555/download/model.onnx --directory-prefix=large_data
wget http://$IP:5555/download/embs.npy   --directory-prefix=large_data
sudo docker-compose up
