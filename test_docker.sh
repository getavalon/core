docker run --rm --name avalon-mongo -d mongo
: <<'END'
docker run \
	--rm \
	-v /$(pwd):/workspace \
	--link avalon-mongo:mongo \
    -e COVERALLS_REPO_TOKEN \
    -e TRAVIS_JOB_ID \
	-e AVALON_SILENT \
	-e AVALON_MONGO=mongodb://mongo:27017 \
	avalon/maya
END
docker run \
	--rm \
	-v /$(pwd):/workspace \
	--link avalon-mongo:mongo \
	-e AVALON_SILENT \
	-e AVALON_MONGO=mongodb://mongo:27017 \
	avalon/cgwire

docker kill avalon-mongo
