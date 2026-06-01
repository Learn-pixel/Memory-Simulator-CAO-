# Memory Hierarchy Visual Simulator

A Python-based visual simulator that demonstrates how a computer's memory hierarchy works using Cache Memory, Main Memory (RAM), and Virtual Memory.

## Features

* Interactive GUI built with Tkinter
* Adjustable memory access times using sliders
* Configurable cache hit rate and page presence probability
* Simulates:

  * Cache Hits
  * Cache Misses
  * Page Faults
* Real-time calculation of:

  * Cache Hit Ratio
  * Page Fault Rate
  * Average Memory Access Time (AMAT)
* Dynamic visualization using Matplotlib
* Run single or multiple random memory accesses
* Live statistics dashboard

## Technologies Used

* Python
* Tkinter
* Matplotlib

## How It Works

The simulator models memory access using probability-based outcomes:

1. A memory request is generated.
2. The simulator checks if it results in a cache hit.
3. If the cache misses, it checks whether the required page is present in main memory.
4. If the page is not present, a page fault occurs and virtual memory is accessed.
5. Statistics and graphs are updated in real time.

## Metrics Displayed

* Total Memory Accesses
* Cache Hits
* Cache Misses
* Page Faults
* Cache Hit Ratio
* Page Fault Rate
* Average Memory Access Time (AMAT)

## Running the Project

Install the required dependencies:

```bash
pip install matplotlib
```

Run the application:

```bash
python memory_hierarchy_full_simulator.py
```

## Educational Purpose

This project helps students understand:

* Memory hierarchy concepts
* Cache performance
* Page faults
* Memory access latency
* Average Memory Access Time (AMAT)

## Author

Nikita Nath
