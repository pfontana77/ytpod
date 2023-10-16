### README.MD for "ytpod" Project

---

# ytpod: Your YouTube Podcast Downloader

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Installation](#installation)
  - [Dependencies](#dependencies)
  - [Docker](#docker)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

---

## Description

`ytpod` is a Python application that allows you to download episodes from a YouTube channel and manage an RSS feed through a web server. The application utilizes Flask and other Python libraries to provide a smooth and functional user experience.

It's still in early alpha and not intended to be used as is.

---

## Features

- Download episodes from a YouTube channel
- Automatically update RSS feed
- Integrated web server to serve files and feeds
- Scheduled tasks for automated operations
- Docker support

---

## Installation

### Dependencies

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

### Docker

If you prefer using Docker, you can follow the instructions in the `compose.yaml` and `Dockerfile`.

---

## Usage

1. Start the web server:

```bash
python app.py
```

2. To download episodes from a specific YouTube channel, run:

```bash
python download_episodes_from_channel.py
```

3. To update the RSS feed:

```bash
python rss.py
```

---

## Contributing

If you wish to contribute to the project, feel free to open a Pull Request or report issues through GitHub's "Issues" section.

---

## License

This project is distributed under the MIT License. For more details, please refer to the `LICENSE` file.
