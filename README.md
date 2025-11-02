# museum-mgr
A museum manager. Goal: correlate the tourist attendance at their museums with the population of the respective cities.

# Systems requirements:
- uv
- just

# Running the program:
    `uv run python main.py {POPULATION_NUMBER}` ie: `uv run python main.py 10_000`

# Running inside docker/podman (mounting the cache directory to avoid re-fetching the data):
    `docker build -t museum-mgr .` 
    `docker run -v /Users/mjacques/code/museum-mgr/cache:/app/cache museum-mgr {POPULATION_NUMBER}`

# Tasks: 
- Build a harmonized database with the characteristics of museums and the population of the cities where they are located.
- Create a small linear regression ML algorithm to correlate the city population and the influx of visitors.

# Other:
- The list of museums is at: https://en.wikipedia.org/wiki/List_of_most-visited_museums
- Balance the need for quickly assessing the data, rapid prototyping and deploying a MVP to a (potentially) public user that could later scale.
- Use the Wikipedia APIs to retrieve this list of museums and their characteristics.
- Choose the source of your choice for the population of the cities concerned.