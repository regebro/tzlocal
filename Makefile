root_dir := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
bin_dir := $(root_dir)/ve/bin

all: devenv test

# The fullrelease script is a part of zest.releaser, which is the last
# package installed, so if it exists, the devenv is installed.
devenv:	ve/bin/fullrelease

ve/bin/fullrelease:
	virtualenv ve
	$(bin_dir)/pip install -e .[devenv]

update_mapping:
	$(bin_dir)/python update_windows_mappings.py

check:
	$(bin_dir)/black tzlocal tests
	$(bin_dir)/flake8 tzlocal tests
	$(bin_dir)/pyroma -d .

coverage:
	$(bin_dir)/coverage run $(bin_dir)/pytest
	$(bin_dir)/coverage html
	$(bin_dir)/coverage report

test:
	$(bin_dir)/pytest

release: update_mapping check
	$(bin_dir)/fullrelease

clean:
	rm -rf ve .coverage htmlcov build .pytest_cache
