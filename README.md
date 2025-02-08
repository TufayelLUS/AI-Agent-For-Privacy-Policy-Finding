# AI Agent For Privacy Policy Link Finding & Summary Generator Tool
This Python & Ollama powered AI agent finds privacy policy links and gives a summary of the page automatically

# Library Installation
```bash
pip install requests bs4 openai fuzzywuzzy python-Levenshtein
```

# Concept
This takes a link from the user that should ideally be the homepage of a website. It then accesses the website and parses the hyperlinks from the page using the beautiful soup library. Then it uses a fuzzy string matching algorithm to detect mostly matched privacy policy links from the <code>to_find</code> keyword list and returns it. Then the page text is summarized using Ollama local API via openai library wrapper and displayed to the user. 

# Other Use Cases
This can be changed to find terms of service/contact us page or other scenarios too. It's a proof of concept(POC) implementation of the agent with minimal functionalities now. 
