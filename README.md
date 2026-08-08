```
Checks both known LLM headers such as:
       - claudebot
       - claude-web-fetcher
       - chatgpt-user
       - gptbot
       - perplexitybot
       - youbot
       - coherebot
       - python-httpx
       - python-requests
       - headlesschrome
       - langchainbot
       - applebot
       - googlebot

and also the lack of common user browser headers
also checks if request rate is inhuman

Uses fastapi's Requests class.
```
