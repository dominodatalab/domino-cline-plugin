# Domino Experiment Setup

Set up MLflow experiment tracking for traditional machine learning projects
in Domino. Invoke with `/domino-experiment-setup` (optionally followed by an
experiment base name, e.g. `/domino-experiment-setup my-model-training`).

## Steps

1. **Scan the project** for ML framework dependencies (requirements.txt,
   pyproject.toml, imports) — sklearn, xgboost, tensorflow, pytorch, lightgbm.
2. **Create `experiment_setup.py`** with unique experiment naming and
   auto-logging for whichever frameworks were detected.
3. **Add Domino context** as MLflow tags (user, project, run ID, hardware tier).
4. **Create or update an example training script** demonstrating the setup.

If run with no argument, ask for an experiment base name before generating
files.

## experiment_setup.py

```python
"""Domino Experiment Tracking Setup"""

import mlflow
import os

def setup_experiment(base_name: str = "experiment"):
    """
    Set up a Domino-compatible MLflow experiment.

    IMPORTANT: Experiment names must be unique across the entire
    Domino deployment. This function appends username and project
    to ensure uniqueness.
    """
    username = os.environ.get('DOMINO_STARTING_USERNAME', 'unknown')
    project = os.environ.get('DOMINO_PROJECT_NAME', 'unknown')

    # Create unique experiment name
    experiment_name = f"{base_name}-{project}-{username}"

    mlflow.set_experiment(experiment_name)
    print(f"Experiment set: {experiment_name}")

    return experiment_name

def log_domino_context():
    """Log Domino environment information as tags."""
    mlflow.set_tags({
        "domino.user": os.environ.get('DOMINO_STARTING_USERNAME', 'unknown'),
        "domino.project": os.environ.get('DOMINO_PROJECT_NAME', 'unknown'),
        "domino.run_id": os.environ.get('DOMINO_RUN_ID', 'unknown'),
        "domino.hardware_tier": os.environ.get('DOMINO_HARDWARE_TIER_NAME', 'unknown'),
    })

def setup_autolog():
    """Enable auto-logging for detected ML frameworks."""
    try:
        import sklearn
        mlflow.sklearn.autolog()
        print("Enabled sklearn auto-logging")
    except ImportError:
        pass

    try:
        import tensorflow
        mlflow.tensorflow.autolog()
        print("Enabled TensorFlow auto-logging")
    except ImportError:
        pass

    try:
        import torch
        mlflow.pytorch.autolog()
        print("Enabled PyTorch auto-logging")
    except ImportError:
        pass

    try:
        import xgboost
        mlflow.xgboost.autolog()
        print("Enabled XGBoost auto-logging")
    except ImportError:
        pass

    try:
        import lightgbm
        mlflow.lightgbm.autolog()
        print("Enabled LightGBM auto-logging")
    except ImportError:
        pass
```

## Example usage in a training script

```python
# train.py
from experiment_setup import setup_experiment, log_domino_context, setup_autolog
import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris

# Setup
experiment_name = setup_experiment("iris-classifier")
setup_autolog()

# Load data
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42
)

# Train with MLflow tracking
with mlflow.start_run(run_name="random-forest-v1"):
    log_domino_context()
    mlflow.log_param("custom_param", "value")

    model = RandomForestClassifier(n_estimators=100, max_depth=5)
    model.fit(X_train, y_train)

    test_accuracy = model.score(X_test, y_test)
    mlflow.log_metric("test_accuracy", test_accuracy)

    print(f"Test accuracy: {test_accuracy:.4f}")
    print(f"Run ID: {mlflow.active_run().info.run_id}")
```

## Important notes

**Experiment name uniqueness is CRITICAL**: experiment names must be unique
across the entire Domino deployment, not just the current project. The
generated code appends username and project automatically to enforce this —
don't remove that when customizing.

**Large artifact upload** (LLMs, deep learning checkpoints) needs multipart
upload enabled:
```python
os.environ['MLFLOW_ENABLE_PROXY_MULTIPART_UPLOAD'] = "true"
os.environ['MLFLOW_MULTIPART_UPLOAD_CHUNK_SIZE'] = "104857600"  # 100MB
```

## Related

- `/domino-trace-setup` - Set up GenAI tracing instead (for LLM/agent projects).
- `/domino-app-init` - Initialize a web application.
- `domino-experiment-tracking` skill - Deeper MLflow reference (comparing
  runs, model registry) used alongside this.
