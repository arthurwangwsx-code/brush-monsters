# Brush Monsters QA Workspace

This is a standalone prototype and reproducible browser acceptance workspace.
Use ispec for change workflow and validation when available.

- `index.html`: exact standalone deliverable, without a PWA registration.
- `pwa/`: the same game CSS/JavaScript logic split into a PWA test site.
- `tests/test_real_origin.py`: real Chrome, real HTTP origin and localStorage tests.
- `tests/test_pwa.py`: offline install / reload / resume tests.
- `tests/test_pwa_update.py`: cache version migration, cross-app isolation, updates.

Always run the browser tests after modifying the game. Do not consider these tests
equivalent to iPhone Safari hardware acceptance.

