# YouTube Intelligence

A web application designed to analyze YouTube channels and videos using data-driven insights and AI-powered summaries.

---

## Overview

**YouTube Intelligence** allows users to search, analyze, and track YouTube channels and videos.
It combines the **YouTube Data API** with **AI models** to generate meaningful insights, engagement analysis, and intelligent summaries.

---

## Features

### Channel Search

* Search YouTube channels by:

  * Channel name
  * `@handle`
* Uses the **YouTube Data API** to retrieve accurate channel data.

---

### Channel Analysis

* Extract detailed channel information
* Generate an **AI-powered overview** of the channel
* Analyze:

  * Engagement trends
  * Channel profile and content strategy

---

###  Video Search & Extraction

* Fetch all videos from a specific channel
* Search for a specific video by URL
* Retrieve video metadata using the YouTube API

---

### AI Video Insights

* Generate **AI summaries for each video**
* Powered by **Hugging Face models**
* Understand:

  * Content meaning
  * Key topics
  * Overall message

---

### Engagement Tracking

* Track video performance over time
* Visualize metrics such as:

  * Views
  * Likes
  * Engagement trends
* Helps identify high-performing content

---

## Tech Stack

### Backend

* Python
* FastAPI
* YouTube Data API
* Hugging Face (Transformers / Inference API)

### Frontend

* React

### Data Visualization

* Custom charts for engagement tracking

---

## How It Works

1. User searches for a channel or video
2. The app fetches data using the YouTube API
3. AI models generate summaries and insights
4. Metrics are tracked and visualized for analysis

---

## Author

**Cesar Lopez Portillo**

---

This project is open-source and available under the MIT License.
