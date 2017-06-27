docker run \
	--rm \
	-v $(pwd):/workspace \
	--link avalon-mongo:mongo \
	-e AVALON_SILENT \
	-e AVALON_MONGO=mongodb://mongo:27017 \
	-e PYTHONPATH=/workspace:/usr/local/lib/python2.6/site-packages \
	--entrypoint mayapy \
	--workdir /workspace/docs \
	avalon/core \
	-m sphinx source build -E -v