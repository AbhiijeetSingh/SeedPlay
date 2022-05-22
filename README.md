# SeedPlay

A simple program to stream files to mpv from your seedbox.

# Prerequisites
The program requires the following packages:
bs4, requests, inquirerpy and mpv(in PATH).

# User 
create a file named config.json with your seedbox credentials in the following format:
```
{
    "username": "yourusername",
    "password": "yourpassword",
}
```
Run the main.py script to start the program.
The program can navigate through the seedbox directory and play the files.