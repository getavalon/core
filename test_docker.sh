docker run \
	--rm \
	-v $(pwd):/workspace \
	--link mindbender-mongo:mongo \
	-e MINDBENDER_MONGO=mongodb://mongo:27017 \
	pyblish/mindbender