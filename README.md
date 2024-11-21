![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
[![log github events](https://github.com/software-students-fall2024/4-containers-this-container/actions/workflows/event-logger.yml/badge.svg)](https://github.com/software-students-fall2024/4-containers-this-container/actions/workflows/event-logger.yml)
[![Machine Learning Client CI](https://github.com/software-students-fall2024/4-containers-this-container/actions/workflows/ml-client.yml/badge.svg)](https://github.com/software-students-fall2024/4-containers-this-container/actions/workflows/ml-client.yml)
[![Web Application CI](https://github.com/software-students-fall2024/4-containers-this-container/actions/workflows/web-app.yml/badge.svg)](https://github.com/software-students-fall2024/4-containers-this-container/actions/workflows/web-app.yml)

# Containerized App Exercise
## Introduction

In this project, we have three Docker containers: MongoDB, machine-learning-client, and web-app. The system allows users to upload audio files, identify their genres, and provides statistics about their musical preferences along with music recommendations.

Users can register and log in to the web-app, then upload their music through an upload feature or by using the microphone function. The machine-learning-client then classifies the uploaded music into one of the following ten genres: blues, classical, country, disco, hiphop, jazz, metal, pop, reggae, or rock, and returns the result to the user. After that, users can view statistics of all their uploaded music on their main page and receive music recommendations based on their preferences.

## Team

- [Ziqiu (Edison) Wang](https://github.com/ziqiu-wang)
- [Thomas Chen](https://github.com/ThomasChen0717)
- [An Hai](https://github.com/AnHaii)
- [Annabella Lee](https://github.com/annabellalee0113)

## Installation

__Prerequisite__: 
Before running this application, ensure that you have the following installed:

- Docker: [Installation Guide](https://docs.docker.com/get-docker/)
- Docker Compose: [Installation Guide](https://docs.docker.com/compose/install/)
- Python 3.9 or higher (for local testing)

__ToDo__:

1.  Access
- docker-compose up --build
- Go to http://localhost:5002 
- Stop: docker-compose down

2. test
- cd web-app
- pip install -r requirements.txt
- pip install pytest
- pytest