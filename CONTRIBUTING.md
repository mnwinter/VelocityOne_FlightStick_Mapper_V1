# Contributing

Thanks for helping original-V1 owners build reliable setups. This is an independent preview project, licensed GPL-3.0-only; dependencies retain their own licenses.

## Before changing code

Open an issue for a substantial feature or behavior change. Describe the problem, expected behavior and relevant hardware/game context. Keep changes focused and preserve existing profiles, calibration, macros and stop/release behavior. Do not commit personal profiles, logs, downloaded build payloads or credentials.

## Local checks

Use Windows 11 x64 and Python 3.12. From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

For packaging, follow the dependency fetch and build steps in [README](README.md). Fetching dependencies does not authorize installing drivers. Driver installation is an explicit administrator action.

## Pull requests

Explain the problem, the resulting behavior and how you verified it. Add regression coverage for logic changes. For UI changes, inspect actual rendered screenshots for readability and overlap; state when that check was blocked. Keep keyboard/mouse ownership balanced and cancel output on stop, disconnect and edits. Validate imported profiles before activating them and never silently overwrite another preset.

Unit tests and CI do not prove USBIP attachment, physical-device behavior, game compatibility or anti-cheat acceptance. Label evidence precisely: mocked protocol, real driver attachment, measured hardware, or a named game/control scheme. Do not invent button numbers or present proposed starter layouts as verified game defaults.

Only submit artwork and code you have permission to license. Public assets must remain original; manufacturer photographs are excluded. Preserve third-party license notices and corresponding-source information. Contributions are provided under this project's GPL-3.0-only license.
