FROM mottosso/maya:2016sp1

RUN wget https://bootstrap.pypa.io/get-pip.py && \
	mayapy get-pip.py && \
	mayapy -m pip install \
		nose \
		nose-exclude \
		coverage \
		pyblish-base==1.4.2 \
		pyblish-maya \
		pymongo \
		# Sphinx 1.8.0 fail to build doc, pin version to 1.7.9
		# see https://github.com/sphinx-doc/sphinx/issues/5417
		sphinx==1.7.9 \
		six \
		sphinxcontrib-napoleon \
		python-coveralls

# Avoid creation of auxilliary files
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /workspace

ENTRYPOINT \
	PYTHONPATH=$(pwd):$PYTHONPATH mayapy -u run_maya_tests.py && \
	mayapy -c "import sys, os, coveralls;coveralls.wear() if os.getenv('TRAVIS_JOB_ID') else sys.stdout.write('Skipping coveralls')"
