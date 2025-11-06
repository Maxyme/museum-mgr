# museum-mgr
A museum manager. Goal: correlate the tourist attendance at their museums with the population of the respective cities.

# Systems requirements:
- uv
- just

# Running the program:
    `uv run python main.py {POPULATION_NUMBER}` ie: `uv run python main.py 10_000`

# Running inside docker/podman (mounting the cache directory to avoid re-fetching the data):
    `docker build -t museum-mgr .` 
    ` docker run -v "$(PWD)/cache:/app/cache" museum-mgr 100_000`

# Running jupyter notebook:  
    `docker pull jupyter/scipy-notebook:latest`
    `docker run -it --rm -p 8888:8888 -v "$(PWD)":/home/jovyan/work quay.io/jupyter/scipy-notebook` 

# Running Jupyter Notebook for Model Analysis:

First, ensure you have run the main program at least once to generate the model and cache data.

## Build the Jupyter Docker image:
    `docker build -t museum-mgr-jupyter -f Dockerfile.jupyter .`

## Run Jupyter Notebook with cache mounted:
    `docker run -p 8888:8888 -v /Users/mjacques/code/museum-mgr/cache:/home/jovyan/work/cache museum-mgr-jupyter`

Then open your browser to `http://localhost:8888` and open `model_details.ipynb` to explore the model.

The notebook includes:
- Model information and architecture
- Model coefficients and equation
- Test predictions
- Visualization of the regression line
- Performance metrics (MSE, RMSE, MAE, R²)
- Residual analysis
- City rankings by museum visitors

**Note:** This uses the `jupyter/scipy-notebook` Docker image which includes Jupyter, matplotlib, numpy, scipy, and pandas pre-installed. ONNX packages are installed on top of it.


# Tasks: 
- Build a harmonized database with the characteristics of museums and the population of the cities where they are located.
- Create a small linear regression ML algorithm to correlate the city population and the influx of visitors.

# Other:
- The list of museums is at: https://en.wikipedia.org/wiki/List_of_most-visited_museums
- Balance the need for quickly assessing the data, rapid prototyping and deploying a MVP to a (potentially) public user that could later scale.
- Use the Wikipedia APIs to retrieve this list of museums and their characteristics.
- Choose the source of your choice for the population of the cities concerned.