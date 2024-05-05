from utils.pipeline import LazyPipe

# Define the pipelines to run
pipes = ["deployment"]

for pipe in pipes:
    lazypipe = LazyPipe(pipe=pipe)
    lazypipe.magic()
