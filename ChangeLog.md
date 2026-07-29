# Changelog

## [0.1.9] - 2026-07-29

- Dependencies updated.
- Bug fix: Dusts on Junana front side is resolved.

## [0.1.8] - 2026-06-24

- JupyterLite updated. Now Pyodide 314.0.0!
- Fix: cmm-16bit 0.1.8 was corrupted for printing ICC profile.

## [0.1.7] - 2026-06-23

- Now Pyodide ready. `safetensors` is replaced by `np.savez_compress()`. `pikepdf` is replaced by `pypdf`.
- Now Jupyter ready. `from keycap_designer.jupyter import *` and `show_inline([Manuscript])` etc.
- Now JupyterLite in Github Pages is available. See `jupyterlite/`.
- `trim` added to `Style`. Now you can print legends on margin area.

## [0.1.6] - 2025-12-23

- Now Python 3.14 ready.
- Breaking change: `v_o=Top` behavior has been changed. The old behavior made inconsistent layout.
- `Affine` added.
- Now `device_rgb_as_cv2_to_workspace` can choose BPC behavior.

## [0.1.5] - 2025-07-15

- Security fix: Follows [CVE-2025-48379](https://nvd.nist.gov/vuln/detail/CVE-2025-48379) of Pillow.

## [0.1.4] - 2025-06-24

- Bug fix: `DeviceRGBColor` should be used with `Relative`.

## [0.1.3] - 2025-06-24

- The common use scenario has been changed to pip based.
- `DeviceRGBColor` added.

## [0.1.2] - 2023-11-27

- Initial release
