# FastAPIHomework

## Description
### Welcome! This is 2022 MVCLab Summer training homework, it is a linebot capable of being calculator and doing expenses and income recorder.

### Setup Guide
* **How to run**
    * **How to run**
    * **Step 0: Go to main path**
        * > cd ./LineBotHomework
    * **Step 1: Install Python Packages**
        * > pip install -r requirements.txt
    * **Start ngrok https server (default port:8787)**
        * > ngrok http 8787
        * > http://127.0.0.1:4040
    * **Step 2: Run main.py by uvicorn (default localhost:8787)**
        * > python main.py
### Supported Operation: Calculator
* **Addition**
    * > __decimal__ + __decimal__ 
    * **or** 
    * > __decimal__ + __decimal__ =
* **Subtraction**
    * > __decimal__ - __decimal__ 
    * **or** 
    * > __decimal__ - __decimal__ =
* **Multiplication**
    * > __decimal__ * __decimal__ 
    * **or** 
    * > __decimal__ * __decimal__ =
* **Division**
    * > __decimal__ / __nonzero_decimal__ 
    * **or** 
    * > __decimal__ / __nonzero_decimal__ =
* **Study Quote Motivation**
    * > #quote


### Supported Operation: Expense recorder
* **Add data**
    * > #note __event__ (+/-) __decimal__
* **Print all data**
    * > #report
* **Remove certain event data**
    * > #delete
* **Sum data from now until desired duration**
    * > #sum __duration__, e.g. #sum 1d = sum expenses from now until 1 day prior
* **For complete instruction manual, and all  supported time duration for #sum, please enter:**
    * > #help

