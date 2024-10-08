
Makeflags += --silent

HOME_DIR = $(HOME)
LOC_FILE = $(HOME_DIR)/.loc.json

define ReadLoc
$(shell node -p "require('$(LOC_FILE)').$(1)")
endef

# project dirs
SRC_DIR = src
BIN_DIR = bin
LIB_DEP = library
CONF_DIR = config

APP = src-installer

# if install or uninstall is called, check if the directories exist
ifneq ($(filter install uninstall, $(MAKECMDGOALS)),)
$(if $(call ReadLoc, bin),,$(error ensure there is a .loc.json file in the home directory. if not run `make loc`))
endif

# system-wide dirs
HOME_DIR = $(HOME)
PATH_BIN_DIR = $(call ReadLoc,bin)
PATH_LIB_DEP = $(call ReadLoc,library)/$(APP)
PATH_CONF_DIR = $(call ReadLoc,config)/$(APP)

PYTHON = python3
PYFLAGS = -p "/usr/bin/env python3" -o $(BIN_DIR)/$(APP) -c

.PHONY: build
build: clean
	echo "building $(APP)..."
	mkdir -p $(BIN_DIR)
	$(PYTHON) -m zipapp $(SRC_DIR) $(PYFLAGS)
	chmod +x $(BIN_DIR)/$(APP)
	echo "done."

.PHONY: init
init:
	echo "initializing project..."
	mkdir -p $(BIN_DIR)
	mkdir -p $(LIB_DEP)
	mkdir -p $(CONF_DIR)
	echo "done."

.PHONY: deps
deps:
	echo "downloading dependencies into the source directory"
	$(PYTHON) -m pip install -r requirements.txt --target $(SRC_DIR)

.PHONY: clean
clean:
	echo "cleaning local bin directory..."
	rm -rf $(BIN_DIR)
	echo "done."

.PHONY: install
install: uninstall
	echo "installing $(APP)..."
	mkdir -p $(PATH_BIN_DIR)
	mkdir -p $(PATH_LIB_DEP)
	mkdir -p $(PATH_CONF_DIR)
	echo "copying files..."
	cp -r $(BIN_DIR)/$(APP) $(PATH_BIN_DIR) 2>/dev/null || :
	cp -r $(LIB_DEP)/* $(PATH_LIB_DEP) 2>/dev/null || :
	cp -r $(CONF_DIR)/* $(PATH_CONF_DIR) 2>/dev/null || :
	rmdir $(PATH_LIB_DEP) 2>/dev/null || :
	rmdir $(PATH_CONF_DIR) 2>/dev/null || :
	echo "done."

.PHONY: uninstall
uninstall:
	echo "uninstalling $(APP)..."
	rm -f $(PATH_BIN_DIR)/$(APP)
	rm -rf $(PATH_LIB_DEP)
	rm -rf $(PATH_CONF_DIR)
	echo "done."

.PHONY: help
help:
	help:
		@echo "Usage: make [target]"
		@echo ""
		@echo "Targets:"
		@echo "  build       - Compile the project"
		@echo "  deps        - Download pip dependencies"
		@echo "  clean       - Clean all object files"
		@echo "  install     - Install the project"
		@echo "  uninstall   - Uninstall the project"
		@echo "  help        - Display this help message"
