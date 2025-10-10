# 🔗 url_extractor

Extract URLs from a text file, filter by domain, and save results — small reusable module.

---

## Features
- Read text file and extract http/https URLs
- Filter URLs by domain (substring match)
- Optionally only write unique URLs (preserves original order)
- Usable as a module or CLI: `python -m url_extractor -c config.yaml`

---

## 📂 Project Structure

```
url_extractor/
│
├── __init__.py
├── __main__.py
├── cli.py
├── core.py
├── config.example.yml
└── README.md
```

---

## Use
```bash
cd py-scripts
python -m url_extractor -c ./url_extractor/defaults.yaml
````

Or import in Python:

```py
from url_extractor.core import extract_urls_from_file, filter_urls_by_domain, write_urls_to_file

urls = extract_urls_from_file("data/source.txt")
urls = filter_urls_by_domain(urls, "udemy.com")
write_urls_to_file(urls, "data/udemy_urls.txt", unique=True)
```

---

## Config (YAML)

See `config.example.yaml` for an example.
