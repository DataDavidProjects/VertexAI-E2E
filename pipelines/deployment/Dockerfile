FROM europe-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-3:latest


WORKDIR /

RUN mkdir /deployment
COPY pipelines/deployment/ /deployment/


RUN pip install --upgrade pip 
RUN cd /deployment/ && pip install -e .

ENV FLASK_APP=/deployment/app/app.py
# Expose port 8080
EXPOSE 8080
ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--port=8080"]