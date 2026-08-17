.PHONY: build up setup release help

help:
	@echo "Targets:"
	@echo "  build                   Build oathsworn-webapp container image"
	@echo "  build INCLUDE_GERMAN_LANG=true  Build with German language support"
	@echo "  up                      Start container with docker compose"
	@echo "  setup                   Alias for build"
	@echo "  release VERSION=vX.Y.Z  Tag and push a release"

build:
	INCLUDE_GERMAN_LANG=$(INCLUDE_GERMAN_LANG) ./setup.sh

up:
	docker compose up -d

setup: build

release:
ifndef VERSION
	$(error VERSION is required, e.g. make release VERSION=v0.1.0)
endif
	@git diff --quiet || (echo "Error: uncommitted changes - commit or stash first"; exit 1)
	@git diff --cached --quiet || (echo "Error: staged changes - commit or stash first"; exit 1)
	git tag -a $(VERSION) -m "Release $(VERSION)"
	git push origin $(VERSION)
	@echo ""
	@echo "Tag $(VERSION) pushed. Open to publish the release:"
	@echo "  https://github.com/TheTacoScott/oathsworn-webapp/releases/new?tag=$(VERSION)"
