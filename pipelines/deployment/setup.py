from setuptools import setup, find_packages

setup(
    name="src",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "google-cloud-bigquery==3.21.0",
        "google-cloud-aiplatform==1.49.0",
        "google-cloud-storage==2.16.0",
        "google-cloud-artifact-registry==1.11.3",
        "kfp==2.7.0",
        "pandas==2.2.2",
        "numpy==1.26.4",
        "scikit-learn==1.4.2",
        "flask==3.0.3",
        "joblib==1.4.0",
        "pyyaml==6.0.1",
        "python-dotenv==1.0.1",
        "pyarrow==16.0.0",
        "probatus==3.1.0",
        "jinja2==3.1.3",
        "mkdocs==1.6.0",
        "black==24.4.2",
        "pre-commit==3.7.0",
    ],
)
