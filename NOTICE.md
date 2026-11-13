# Credits and license status

The manual preview reuses existing sources and obtains its dependencies
separately. Each project's license text and copyright notices remain applicable.

| Component | Origin / license notes |
| --- | --- |
| KDE shell | [ladybug-me/caelestia-kde](https://github.com/ladybug-me/caelestia-kde), pinned in `installation/shell-lock.json`; GPL-3.0-or-later, with license texts in the upstream checkout at `LICENSE` and `shell/LICENSE` |
| Caelestia | [caelestia-dots/shell](https://github.com/caelestia-dots/shell), the basis of the KDE port; its notices remain with the sources |
| Shell overlays and integration patch | Changes to Caelestia-KDE sources, under the GPL terms of the respective source files; includes shared translation integration |
| Window decoration / Qt style | [Bali10050/Darkly](https://github.com/Bali10050/Darkly), version and revision in the component READMEs; retain the upstream license in each build checkout |
| Tiling | Krohnkite from the configured KDE/Caelestia environment; provenance and local changes in `kde-customizations/tiling/` |
| Hermes | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent), a separate checkout pinned by the Hermes installer; upstream and model licenses apply separately |
| Icons | KDE/Breeze and the icon set obtained by the Caelestia-KDE installer; retain the respective upstream licenses |
| Repository organization | [Ryoku](https://github.com/Ryoku-dev/ryoku) as an organizational reference; no Ryoku installer or system profile is included |

Original flausen. code is licensed under GPL-3.0-or-later.
Existing component licenses and third-party notices continue to apply. The
MIT-marked Dolphin folder icons use [the MIT license](LICENSES/MIT.txt).
The license grant for code excludes project trademarks. The 63 final desktop
wallpapers in `kde-customizations/wallpapers/` are included with the project
owner's approval. Other brand artwork and presentation assets with unresolved
rights are omitted from this public source snapshot.
System fonts come from the distribution.

API keys, tokens, chat histories, personal desktop configuration and backups are
not installation payloads. The source snapshot does not bundle gaming clients,
games, commercial applications or their accounts.
