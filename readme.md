
# Web Scraper Project – for stock market

## Project Overview

This project is a web scraping solution developed using **Selenium** and **BeautifulSoup** to extract, process, and structure data from dynamic and static websites.

It has online, desktop (VBA/excel and python), cloud gui

The scraper is designed to handle JavaScript-rendered content, automate browser interactions, and collect structured data efficiently and reliably.

---

## Basic Technologies Used

* **Python**
* **Selenium** – for browser automation and dynamic content handling
* **BeautifulSoup** – for HTML parsing and data extraction
* CSV for data export
* docker and cloud computing

---

## Problem Statement

One particular website for brazilian stock market updated with dynamic content using JavaScript, making traditional scraping methods insufficient. The goal of this project was to:

* Access dynamically loaded data
* Navigate through pagination and interactive elements
* Extract structured information
* Store data in a clean and reusable format

---

## Solution Approach

1. **Browser Automation with Selenium**

   * Launch automated browser sessions
   * Handle login (demandatory)
   * Click buttons and navigate pages
   * Wait for dynamic content to load

2. **HTML Parsing with BeautifulSoup**

   * Extract specific elements (tables, listings, links, metadata)
   * Clean and normalize data
   * Handle missing or inconsistent fields

3. **Data Processing**

   * Remove duplicates
   * Format structured datasets
   * Export to CSV
   * Financial Analysis in order to generate investment recommendations

*******************************************

## Key Features

* Handles dynamic JavaScript content
* Automatic waiting and error handling
* Modular and reusable code structure
* Scalable for large datasets
* Logging and exception management

---

## Challenges & Solutions

* **Dynamic content loading** → Implemented explicit waits with Selenium
* **Anti-bot detection** → Managed request timing and browser configuration
* **Data inconsistency** → Added validation and cleaning functions

---

## Results

* Reliable extraction of structured data
* Reduced manual data collection time
* Automated repeatable process
* Clean, maintainable, and extensible codebase

---

## Development time

  Aprox five months
  two people time (one finance and other AI/TI  focus)
---

|   |  |
|---|--|
|output |![database sample ](/code/imagens/output.png)| 
|input sample |![comparative sample ](/code/imagens/webgui.png)| 
