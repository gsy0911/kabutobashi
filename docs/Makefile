# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build
PACKAGEDIR    = kabutobashi
PACKAGEGUIEDE = guide

# Put it first so that "make" without argument is like "make help".
help:
	@echo " == simple make == "
	@echo "type 'make clean docstring html' to build documentation file"
	@echo ""
	@echo " == command references == "
	@echo "clean: clean build directory"
	@echo "docstring: generate python docstring documentation"
	@echo "html: build html file"

.PHONY: help docstring html

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
# %: Makefile
# 	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	-rm -rf $(BUILDDIR)/*

html:
	sphinx-build $(SOURCEDIR) ./$(BUILDDIR)
	@echo "finish"

# options
# --no-headings: Do not create headings for the modules/packages.
# --module-first: Put module documentation before submodule documentation.
docstring:
	sphinx-apidoc --no-headings --module-first -f -o $(PACKAGEGUIEDE) ../$(PACKAGEDIR)
	@echo "finish"
