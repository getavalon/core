docker run \
  --rm \
  --volume $(pwd):/workspace \
  --link avalon-mongo:mongo \
  --env AVALON_SILENT \
  --env AVALON_MONGO=mongodb://mongo:27017 \
  --env PYTHONPATH=/workspace:/usr/local/lib/python2.6/site-packages \
  --entrypoint mayapy \
  --workdir /workspace/docs \
  avalon/core:maya \
  -m sphinx source build -E -v
