# Project description

This horse racing form app is a personal folio project designed to demonstrate data engineering skills, particularly the implementation of a medallion architecture and the creation of robust pipelines using Python, as well as basic front-end skills through the development of a UI. The app is strictly non-commercial and not intended for use beyond showcasing technical capability.

# Technical diagram

![alt text](https://github.com/dventura11997/horse-form-sv-app/blob/main/doco/tech_diagram.jpg?raw=true)

# How-to doco

This piece of the doco explains how the code functions:

- The app.py file contains the streamlit wrapper
- It imports the data engineering functions from the functions.py file (this contains all the data engineering functions)
- The get_raw_data, raw_to_trn and trn_to_int is to demonstrate knowledge of medallion architecture and occassionally for testing