
# Run Maya test
docker run \
  --rm \
  --volume $(pwd):/workspace \
  --link avalon-mongo:mongo \
  --env AVALON_SILENT \
  --env AVALON_MONGO=mongodb://mongo:27017 \
  --env TRAVIS_JOB_ID \
  --env TRAVIS_BRANCH \
  --env COVERALLS_REPO_TOKEN \
  avalon/core:maya
# Rename coverage data file and will be combined later
mv .coverage .coverage.maya

# docker run other DCC tools..
