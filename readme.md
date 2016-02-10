# Lego Collection Value

A Python script that checks your Brickset owned/wanted sets vs. BrickLink price information to give you an idea of their value.

This script uses Python 2.7.6, the suds SOAP library, and robbietjuh's py-bricklink library

Note: I'm terrible at Python but it's fun, so ¯\\\_(ツ)_/¯

To run the script, you'll need a Brickset API key and BrickLink consumer keys and secrets.  Your Brickset owner/wanted lists will also have to be publicly accessible.

You can add the following to `keys.json`, or manually input it at the command line:

    {
      "brickset_api_key" : "asdf-1234-qwer",
      "bricklink_consumer_key" : "KEY",
      "bricklink_consumer_secret" : "SECRET",
      "bricklink_access_token" : "TOKEN",
      "bricklink_access_token_secret" : "TOKEN_SECRET"
    }

Sample output:

    ~$ python lcv.py
    
    Loading API keys from keys.json...
    Let's find the value of your collection and the sets you want!
    Please input the parameters below.
    Brickset Username: Rockmaninoff
    New or used value? 'n' for new or 'u' for used: u

    Processing your collection...
    Getting Brickset list of sets...
    Getting BrickLink price info...

    We were able to process 192/201 of the sets you own!
    The minimum value of your collection is: $16,856.39
    The maximum value of your collection is: $32,768.22
    The total average value of your collection is: $21,894.27
    The total quantity average value of your collection is: $21,880.47
    The most valuable set you own is: 10179-1 with a value of $5,039.62

    Processing wanted sets...
    Getting Brickset list of sets...
    Getting BrickLink price info...

    We were able to process 106/121 of the sets you want!
    The minimum value of the sets you want is: $13,599.22
    The maximum value of the sets you want is: $24,097.95
    The total average value of the sets you want is: $17,189.85
    The total quantity average value of the sets you want is: $17,186.01
    The most valuable set you want is: 4000014-1 with a value of $3,300.00