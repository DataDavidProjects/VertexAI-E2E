from utils.pipeline import LazyPipe

# Define the setup for the pipeline
setup = True
# Define the pipelines to run
pipes = ["production"]
for pipe in pipes:
    print(f"Running {pipe} pipeline...")
    lazypipe = LazyPipe(pipe=pipe)
    lazypipe.magic(setup=setup)
