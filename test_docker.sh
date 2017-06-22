docker run \
	--rm \
	-v $(pwd):/workspace \
	--link mindbender-mongo:mongo \
	-e AVALON_SILENT \
	-e AVALON_MONGO=mongodb://mongo:27017 \
	mindbender/core