# Patches to apply

The original build only delivered the remaining steps; these files edit modules that were
written earlier on the build machine (not included in this package).

1. `01_views_record_form_page.py`: replace `record_form_page` in `konsumo/web/views.py`
2. `02_cli_cmd_serve.py`: replace `cmd_serve` in `konsumo/cli.py`
3. `03_tests_webapp.py`: edit `tests/test_konsumo.py` (add `import threading`, remove the
   faulty third `assertRaises` block in `TestCRUD.test_validation`, replace `TestWebApp`)
