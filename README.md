# Why do earthquakes lag behind pressure at Blue Mountain?

The models favour pressure taking time to reach the faults as an explanation for the earthquake delay. Deeper events tend to respond later. This interpretation assumes the pressure and earthquake records share the same clock, which remains uncertain.

This project reanalyses the 2023 geothermal test at Blue Mountain, Nevada. The question: what causes the delay, and could slower pressure rises change it?

The data cannot isolate the effect of rise speed: faster rises also reached higher pressures. Of five cycles, one gives a clear timing signal and another is partly cut off by missing data. In the best model, slower rises to the same pressure produce more earthquakes but a smaller gap between the pressure and earthquake peaks. Those are predictions, not measurements.

## Find your way in

- [FINDINGS.md](FINDINGS.md): detailed results, evidence and a proposed follow-up test.
- [REPORT.md](REPORT.md) and [COMPLETE.md](COMPLETE.md): assessment, open questions and completion record.
- [PROBLEM.md](PROBLEM.md): the original research question.
- [figs/](figs/), [results/](results/) and [blm/](blm/): figures, result files and analysis code.

## Reproduce

Requires Python 3.12, `uv`, `make` and Git. From the repository root:

```sh
uv venv --python 3.12 .venv
uv pip install -r requirements.txt
make all
```

This regenerates the results, figures and three technical documents above. `make light` reuses the saved validation and design runs. [results/manifest.json](results/manifest.json) records the source commit and Python version.

## Sources and licences

- Chamarczuk and colleagues: [OSF data](https://doi.org/10.17605/OSF.IO/D65BA) and [accepted manuscript](https://doi.org/10.1029/2025JB031634), both CC BY 4.0. See [data/README.md](data/README.md) for provenance and file checksums.
- USGS ComCat earthquake records: public domain.
- Iowa Environmental Mesonet: Winnemucca ASOS weather records. No licence is recorded here for these files.

The code is [MIT licensed](LICENSE). Data retain their own licences.
