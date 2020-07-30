
# Run Maya test
docker run \
  --rm \
  --volume $(pwd):/workspace \
  --link avalon-mongo:mongo \
  --env AVALON_SILENT \
  --env AVALON_MONGO=mongodb://mongo:27017 \
  avalon/core:maya
# Rename coverage data file and will be combined later
mv .coverage .coverage.maya

# docker run other DCC tools..
