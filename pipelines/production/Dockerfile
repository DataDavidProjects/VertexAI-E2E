# Multistage Dockerfile to build the production image
FROM europe-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-3:latest

# ARG PIPELINE_NAME to match the pipeline name in the pipelines directory
ARG PIPELINE_NAME 

# Set the working directory
WORKDIR /

# copy the pipeline code to the container
RUN mkdir /${PIPELINE_NAME}
COPY pipelines/${PIPELINE_NAME}/ /${PIPELINE_NAME}/

# Install the pipeline code
RUN pip install --upgrade pip 
RUN cd /${PIPELINE_NAME}/ && pip install -e .

ENV FLASK_APP=/${PIPELINE_NAME}/app/app.py
# Expose port 8080
EXPOSE 8080
ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--port=8080"]