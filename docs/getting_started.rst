Getting Started
===============

Installation
------------

Installing Poetry
^^^^^^^^^^^^^^^^^

pyapi_rts uses Poetry to manage python dependencies and versions.
Installation instructions for your operating system can be found here: `Poetry <https://python-poetry.org/docs/>`__.

After Poetry is installed, the necessary Python version and dependencies can be installed by running the :code:`poetry install` command.

Generate classes from RSCAD components 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before you can use pyapi_rts, you need to generate the classes from the RSCAD components.
These classes are not included in the pyapi_rts distribution.

1. Check the :code:`pyapi_rts/class_extractor/COMPONENTS` directory. If it exisists and is not empty, you can skip this step.
   Otherwise, copy the content of the COMPONENTS directory from the RSCAD distribution to the :code:`pyapi_rts/class_extractor/COMPONENTS` directory.
   On Windows, this directory likely can be found at :code:`C:\Program Files\RTDS\RSCAD FX x.x\MLIB\COMPONENTS`
2. Run :code:`poetry run python ./pyapi_rts/class_extractor/main.py`. For options and more information, see :ref:`Class Extractor Usage<class_extractor>`. 


Check for errors
^^^^^^^^^^^^^^^^

It is recommended to run the unit tests after executing the **ClassExtractor** to ensure no errors occured.
To do this, run :code:`poetry run pytest`.

Examples
--------------

See :ref:`Examples <examples>` for examples of API usage.

   
Development
-----------

Setting up a development environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Update the dependencies: :code:`poetry update` 
2. Run :code:`poetry install`.
3. To open a shell within the virtual environment of the project, run :code:`poetry shell`.
4. Run ClassExtractor.

When using Visual Studio Code, the following extensions are recommended:

- `autodocstring <https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring>`_
- `Coverage Gutters <https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters>`_
- `Python <https://marketplace.visualstudio.com/items?itemName=ms-python.python>`_
- `reStructuredText <https://marketplace.visualstudio.com/items?itemName=lextudio.restructuredtext>`_
- `Jupyter Notebooks <https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter>`_

Testing
^^^^^^^

- Tests: :code:`poetry run pytest`
   Tests use the Python unittest framework.
- Coverage:
   .. code:: bash

      poetry run coverage run --omit */docs/*,*/tests/*,*/generated/*,.eggs/*,*/hooks/* -m pytest
      poetry run coverage report
      poetry run coverage xml

Generating documentation
^^^^^^^^^^^^^^^^^^^^^^^^

The documentation is created using Sphinx, which is a Python documentation generator.
It uses restructured text (reST) as its markup language, a language similar to markdown.
All relevant files for the documentation are located in the :code:`docs` directory.

To generate the documentation, switch to the :code:`docs` directory and run :code:`make html` or :code:`make latex`.
After changes to the API, you can manually delete the :code:`docs/apidoc` directory and regenerate it by running :code:`poetry run sphinx-apidoc ./pyapi_rts/ */tests/* */generated/* -o ./docs/apidoc/make apidoc` from the pyapi_rts directory.

It is not recommended to do this, as the documentation is generated automatically by the pipeline on the main git branch.

GitLab pipeline
^^^^^^^^^^^^^^^

The pipeline defined in .gitlab-ci.yml automates the generation of the documentation, running tests and tracking code coverage.

There are currently four stages in the pipeline:


+----------------+--------------------------------------------------------+-------------+------------+
| Stage          | Description                                            | Condition   | Depends on |
+----------------+--------------------------------------------------------+-------------+------------+
| test           | Run tests and coverage (excluding extensions)          | None        | None       |
+----------------+--------------------------------------------------------+-------------+------------+
| extension-test | Run test including extensions                          | None        | None       |
+----------------+--------------------------------------------------------+-------------+------------+
| pages          | Generate HTML documentation and LateX source           | main branch | test       |
+----------------+--------------------------------------------------------+-------------+------------+
| profiler       | Run a profiler on the tests and generate the call tree | None        | test       |
+----------------+--------------------------------------------------------+-------------+------------+
| docs-pdf       | Run latexpdf on the LateX files from the pages stage   | main branch | pages      |
+----------------+--------------------------------------------------------+-------------+------------+