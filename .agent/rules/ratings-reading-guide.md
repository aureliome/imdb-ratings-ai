---
trigger: always_on
---

The original list of movies I watched and their ratings is saved in the CSV file `data/ratings.csv` and it contains the following columns:
  - `Const`: the ID of the movie on IMDb.com
  - `Your Rating`: the rating I gave to the movie from 1 to 10
  - `Title`: the title of the movie
  - `URL`: the URL of the movie on IMDb.com
  - `Title Type`: the type of the item that can be `Film`, `Serie TV`, and `Mini serie TV`
  - `IMDb Rating`: the average rating (from 1 to 10) of the movie on IMDb.com
  - `Runtime (mins)`: the runtime of the movie in minutes
  - `Year`: the year of the movie
  - `Genres`: the list of the movie's genres, separated by commas
  - `Directors`: the director (or directors in rare cases) of the movie

Consider only films (items with `Title Type == "Film"`); ignore anything else (`Serie TV` and `Mini serie TV`).

The enriched list is saved in the CSV file `data/ratings-plus.csv` and contains extra columns:
  - `Main Actors`: main actors of the movie
  - `Countries`: countries where the movie has been played