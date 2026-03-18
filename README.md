<a href="/img/openMINDS_instances_logo_light.png">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="/img/openMINDS_instances_logo_dark.png">
    <source media="(prefers-color-scheme: light)" srcset="/img/openMINDS_instances_logo_light.png">
    <img alt="openMINDS instances logo: created by U. Schlegel, L. Zehl, C. Hagen Blixhavn" src="/img/openMINDS_instances_logo_light.png" title="openMINDS instances" align="right" height="70">
  </picture>
</a>

# openMINDS_instances

![GitHub][license-url]
![GitHub contributors][contributors-url]

To learn more about the openMINDS metadata framework please go to :arrow_right: [**ReadTheDocs**][docu-url].  
For browsing through the metadata instances you can also directly jump to the :arrow_right: [**instance libraries**][libraries-url].

## How to contribute

The openMINDS metadata framework is an open-source project and community contributions are highly appreciated.  
If you want to contribute please follow our :arrow_right: [**contribution guidelines**][contribution-url].

Explore the coverage statistics for the openMINDS instance library :arrow_right: [**openMINDS instance library coverage**][instance-library-coverage]

## Autopopulation

The autopopulation workflow synchronizes instance files across versions when a `.jsonld` file is added or modified on `main`. The file must be modified in exactly one version per push for triggering the autopopulation.

> To skip autopopulation for a specific push or merge, include `[ci skip-autopopulate]` in the commit message.

### Propagation rules

| Case                                                       | Behavior |
|------------------------------------------------------------|----------|
| Target file exists                                         | File is updated |
| `terminologies/terminology/*` — target file does not exist | Skipped |
| `terminologies/*` — target folder does not exist           | Skipped |
| Top-level folder does not exist in target version          | Skipped |
| Top-level folder exists, subfolder does not                | Subfolder is created and file is propagated |
| Same file modified in multiple versions in a single push   | Skipped for all versions |
| File is moved, renamed  or deleted                         | Not propagated ⚠️ |

### Property synchronization behavior

| Case | Behavior |
|------|----------|
| Property exists in source and is valid for target version | Propagated |
| Property exists in source but not valid for target version | Ignored |
| Property exists in target but not in source | Left untouched |
| Property has the same name but different usage across versions | Propagated ⚠️ |

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contribution-url]: https://openminds-documentation.readthedocs.io/en/latest/shared/contribution_guidelines.html
[contributors-url]: https://img.shields.io/github/contributors/openMetadataInitiative/openMINDS_instances
[docu-url]: https://openminds-documentation.readthedocs.io
[libraries-url]: https://openminds-documentation.readthedocs.io/en/latest/instance_libraries.html
[license-url]: https://img.shields.io/github/license/openMetadataInitiative/openMINDS_instances
[instance-library-coverage]: https://openmetadatainitiative.github.io/openMINDS_instances/