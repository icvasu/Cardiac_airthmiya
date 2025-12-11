# Cardiac Arrhythmia Detection Dashboard (Flask)

A Flask-based web dashboard for detecting and visualizing cardiac arrhythmias from ECG data. This project provides a UI to upload ECG recordings, run a pre-trained model to classify arrhythmia types, and display results and visualizations.

## Features
- Flask web interface for uploading ECG files (CSV / WFDB / numpy)
- Preprocessing pipeline for ECG signals
- Model inference for arrhythmia classification
- Visualization of ECG traces and prediction results
- Simple dashboard with history/log of processed samples

## Requirements
- Python 3.8+
- Flask
- numpy, pandas
- scikit-learn or TensorFlow/PyTorch (depending on model)
- plotting libs: matplotlib / plotly

Install dependencies:
```
pip install -r requirements.txt
```

## Running locally
1. Set up a virtual environment:
```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```
2. Run the app:
```
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
```
Open http://127.0.0.1:5000 in your browser.

## Project structure (high level)
- app.py / run.py — Flask entry point
- templates/ — HTML templates for dashboard
- static/ — CSS, JS, images
- models/ — saved model files
- utils/ — preprocessing and helper functions

## Notes
- Replace model files in models/ with your trained weights.
- Ensure uploaded ECG files match expected sampling rate and channels.

## License
Specify your license here (e.g., MIT).