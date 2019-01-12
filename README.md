# Welcome to the Bounties Twitter bot repo!

This is a simple Serverless application in python, with no state. There is only a single scheduled python function, with a few helpers.

## What it does

- Use the open Bounties API to look for new bounties
- Check the Twitter feed for the bot to look for the most recently posted bounty
- Post new bounties to Twitter

## How to set it up

You will need a `variables.yml` file of your own, containing the following: 
```
TWITTER_API_KEY: ...
TWITTER_API_SECRET_KEY: ...
TWITTER_ACCESS_TOKEN: ...
TWITTER_ACCESS_TOKEN_SECRET: ...
```

When you have this file, all you have to do is `sls deploy` to get the bot up and running. 

Because the bot has no state, it does require there to be existing tweets for the account. Without these tweets, it would not have a starting point to look for new bounties. 