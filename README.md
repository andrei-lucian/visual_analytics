NOTE: Docstrings, the .css theme, and this README were generated with ChatGPT and reviewed by us before being included in the code base.

Bias Detection and Sentiment Analysis Dashboard

This application provides an interactive dashboard for comparing sentiment and bias across multiple sources, including large language models (LLMs), human annotators, and news articles. It extracts keyphrases mentioning a target entity, evaluates their sentiment, and visualizes differences in sentiment and focus to help identify potential bias between sources.
Features

    Extract keyphrases related to a target entity from multiple news articles.

    Analyze sentiment of phrases using pretrained models.

    Visualize sentiment across sources (LLMs, annotators, articles) for easy comparison.

    Identify and highlight potential bias in how different sources represent the same entity.

    Interactive, web-based visualization using Dash and Plotly.

Installation

Create and activate a Python virtual environment (recommended):

python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

Install dependencies:

    pip install -r requirements.txt

Running the Application

Start the application by running:

python run.py

This will launch the Dash web server, typically http://127.0.0.1:8050/
Usage

    Open the provided URL in your web browser.

    Use the interface to select articles, entities, or sources.

    Explore the sentiment visualizations and keyphrase word clouds.

    Compare sentiment differences across annotators, LLMs, and news articles to detect bias.

Requirements

    Python 3.8+

    All Python packages listed in requirements.txt

Notes

    Data files should be located under data/.

    Pretrained models are automatically downloaded via HuggingFace Transformers on first run.

    Ensure internet connectivity during initial setup for model downloads.
