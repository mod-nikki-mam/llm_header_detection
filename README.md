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

along with the lack of common user browser headers, so scrapers need to emulate a full browser
  (which is not impossible,but not trivial and takes more resources in a meaningful way)
also checks if request rate is inhuman

Uses fastapi's Requests class.
```
