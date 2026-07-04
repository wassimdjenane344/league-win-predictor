FROM python:3.11-slim

WORKDIR /ml

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY data ./data

# Trains a model and promotes it to Production inside a container-native
# MLflow file store (MLFLOW_TRACKING_URI=file:///mlruns, a shared volume).
# Runs written here use container-relative artifact paths, so the backend
# container reading the same /mlruns volume can load the model -- unlike a
# host-trained mlruns whose artifact paths are absolute Windows paths.
ENV MLFLOW_TRACKING_URI=file:///mlruns
ENV MLFLOW_MODEL_NAME=lol-win-predictor

CMD ["sh", "-c", "cd src && python train.py --model-type logreg --register && python promote.py"]
