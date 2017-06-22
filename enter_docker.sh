docker run \
	--rm \
	-ti \
	-v $(pwd):/workspace \
	--link avalon-mongo:mongo \
	-e AVALON_SILENT \
	-e AVALON_MONGO=mongodb://mongo:27017 \
	--entrypoint bash \
	avalon/core