# IMDb Ratings AI

Analyze your IMDb ratings history, enrich them with extra information, generate statistics and present them in a presentation (HTML and PDF).

You can see the result in PDF format at [slides/index.pdf](slides/index.pdf) and in HTML format at http://aureliome.github.io/imdb-ratings-ai/.

This project has been developed with the help of [Gemini 3.0](https://gemini.google.com/app) and [Antigravity](https://antigravity.ai/).

## What it does

1. Export ratings from IMDb and save them to [data/ratings.csv](data/ratings.csv)
2. Enrich the original ratings with movies' cast and countries and save them to [data/ratings-plus.csv](data/ratings-plus.csv)
3. Generate statistics (favorite genres/directors/actors, total runtime, and most watched genres) and save them to [stats.json](stats.json)
4. Generate a presentation from the statistics and save it in HTML format to [slides/index.html](slides/index.html) and in PDF format to [slides/index.pdf](slides/index.pdf)

## Try it out

1. Clone the repository
2. Delete the following files:
    - [data/ratings.csv](data/ratings.csv)
    - [data/ratings-plus.csv](data/ratings-plus.csv)
    - [stats.json](stats.json)
    - [slides/index.html](slides/index.html)
    - [slides/index.pdf](slides/index.pdf)
3. Export your IMDb ratings history by navigating to the "Your Ratings" page via your IMDb user profile; and then selecting the "Export" icon from the top right. This will create a `rating.csv` file that you can save to [data/ratings.csv](data/ratings.csv)
4. You can decide to use one of these approaches:
    - **AI Workflows** in your Agent IDE (e.g., Antigravity, Cursor)
        1. Run `/enrich_ratings` to enrich the ratings with actors and countries
        2. Run `/analyze_data` to generate statistics from the ratings
        3. Run `/generate_slides` to generate a presentation from the statistics
    - **Python scripts**
        1. Run `python scripts/enrich_ratings.py` to enrich the ratings with actors and countries
        2. Run `python scripts/analyze_data.py` to generate statistics from the ratings
        3. Run `python scripts/generate_slides.py` to generate a presentation from the statistics
5. You can see your presentation via HTML at [slides/index.html](slides/index.html), or PDF at [slides/index.pdf](slides/index.pdf)

## AI Agent Workflows

- `/enrich_ratings`: Enrich ratings file with main actors and countries, then check the validity of the file.
- `/analyze_data`: Analyze movie ratings and generate statistics, then check the validity of the statistics file.
- `/generate_slides`: Generate a presentation from the calculated statistics.

## Python Scripts

Contained in the `scripts` directory.

- `check_ratings.py`: Validates the `data/ratings-plus.csv` file to ensure it has the required columns and that the data (like ratings and years) is in the correct format.
- `enrich_ratings.py`: Fetch IMDb to get the "Main Actors" and "Countries" for each movie in `data/ratings-plus.csv` (creates it from `data/ratings.csv` if missing) and populates the data into new columns. It handles network errors and saves progress incrementally.
- `analyze_data.py`: Analyzes `data/ratings-plus.csv` to calculate statistics like favorite genres/directors/actors, total runtime, and most watched categories. Outputs JSON stats in `stats.json`.
- `check_stats.py`: Validates the `stats.json` file to ensure valid JSON structure and presence of required fields.
- `generate_slides.py`: Generates an HTML presentation (`slides/index.html`) and a PDF version (`slides/index.pdf`) using the statistics from `stats.json` and a Jinja2 template (`slides/template.html`).

## Files Tree

```
.
├── .agent/
│   ├── rules.md                # AI Agent rules
│   └── workflows.md            # AI Agent workflows
├── data/
│   ├── ratings.csv             # Original ratings from IMDb
│   └── ratings-plus.csv        # Enriched ratings with actors and countries
├── scripts/
│   ├── analyze_data.py         # Analyzes ratings and generates statistics
│   ├── check_ratings.py        # Validates the ratings file
│   ├── check_stats.py          # Validates the stats file
│   ├── enrich_ratings.py       # Enrich ratings with actors and countries
│   ├── generate_slides.py      # Generates a presentation from the statistics
│   └── tests/                  # Tests for the Python scripts
├── slides/
│   ├── index.html              # HTML presentation
│   ├── index.pdf               # PDF presentation
│   └── template.html           # Jinja2 template for the presentation
├── requirements.txt            # Python dependencies
├── stats.json                  # Statistics generated from the ratings
└── README.md
```