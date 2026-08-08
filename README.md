```
Checks both known LLM headers such as:
        claudebot,
        chatgpt-user,
        python-requests,
        headlesschrome,
        langchainbot,
        applebot,
        googlebot
and also the lack of common user browser headers
also checks if request rate is inhuman

Uses fastapi's Requests class.
```
