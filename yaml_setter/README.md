# 🔧 yaml_setter

A simple Python utility to set values in YAML files using dot notation paths with array index support.  
Read content from any file and insert it at a specific path in a YAML file, creating nested structures automatically.

---

## Features
- Set values in YAML files using dot notation (e.g., `a.b.c`)
- Support for array indices (e.g., `users[0].name`)
- Support for multi-dimensional arrays (e.g., `matrix[0][7]`)
- Automatically creates missing parent directories
- Automatically creates nested structures (dicts/lists)
- Preserves existing YAML content
- Replaces incompatible types when needed
- Clean YAML formatting with proper indentation

---

## 📂 Project Structure

```
yaml_setter/
│
├── __init__.py
├── __main__.py
├── yaml_setter.py
└── README.md
```

---

## ⚡ Usage

### CLI

```bash
python -m yaml_setter <input_file> <yaml_file> <yaml_path>
```

**Arguments:**
- `input_file`: File to read content from (text, markdown, etc.)
- `yaml_file`: Target YAML file path (created if doesn't exist)
- `yaml_path`: Dot notation path with optional array indices

**Examples:**

```bash
# Simple nested path
python -m yaml_setter data.txt config.yaml "database.connection.host"

# Array index
python -m yaml_setter message.txt config.yaml "notifications[0].message"

# Multi-dimensional array
python -m yaml_setter content.md config.yaml "matrix[2][5].data"

# Complex nested structure
python -m yaml_setter readme.md config.yaml "docs.api[0].examples[3].code"
```

### As a Library

```python
from yaml_setter import set_yaml_value

# Set a simple value
set_yaml_value("config.yaml", "app.name", "My Application")

# Set value with array index
set_yaml_value("config.yaml", "users[0].email", "user@example.com")

# Set value in multi-dimensional array
content = "Hello World"
set_yaml_value("data.yaml", "grid[5][10]", content)
```

---

## 📝 Path Syntax

### Simple Keys
```
a.b.c  →  {a: {b: {c: value}}}
```

### Array Indices
```
a.b[0]  →  {a: {b: [value]}}
a.b[5]  →  {a: {b: [null, null, null, null, null, value]}}
```

### Nested Arrays
```
a[0].b  →  {a: [{b: value}]}
a[0][1]  →  {a: [[null, value]]}
```

### Complex Structures
```
users[0].addresses[1].city  →  {
  users: [
    {
      addresses: [
        null,
        {city: value}
      ]
    }
  ]
}
```

---

## 🔄 Behavior

### Creating Structures
- Missing parent directories are created automatically
- Missing YAML file is created with proper structure
- Missing nested paths are created as needed

### Type Conflicts
When setting `a.b.c` but `a.b` already exists as a string:
- The string is replaced with a dict structure
- The value is set at `a.b.c`

Example:
```yaml
# Before
message: "hello"

# After setting message.data = "world"
message:
  data: "world"
```

### Array Extension
Arrays are automatically extended with `null` values:
```yaml
# Setting items[5] = "value" when items is empty
items:
  - null
  - null
  - null
  - null
  - null
  - "value"
```

---

## 💡 Use Cases

### Configuration Management
```bash
# Build config from multiple sources
python -m yaml_setter db_host.txt config.yaml "database.host"
python -m yaml_setter db_port.txt config.yaml "database.port"
python -m yaml_setter api_key.txt config.yaml "services.api.key"
```

### Documentation Generation
```bash
# Insert code examples into structured docs
python -m yaml_setter example1.py docs.yaml "api.endpoints[0].example"
python -m yaml_setter example2.py docs.yaml "api.endpoints[1].example"
```

### Data Pipeline
```bash
# Build structured data from text files
python -m yaml_setter commit_msg.txt pipeline.yaml "commits[0].message"
python -m yaml_setter diff.txt pipeline.yaml "commits[0].changes"
```

---

## 🧪 Examples

### Example 1: Simple Configuration

**Input file (`message.txt`):**
```
Hello, World!
```

**Command:**
```bash
python -m yaml_setter message.txt config.yaml "app.greeting"
```

**Result (`config.yaml`):**
```yaml
app:
  greeting: 'Hello, World!'
```

### Example 2: Array with Index

**Input file (`user.json`):**
```json
{"name": "John", "role": "admin"}
```

**Command:**
```bash
python -m yaml_setter user.json config.yaml "users[0].data"
```

**Result (`config.yaml`):**
```yaml
users:
  - data: '{"name": "John", "role": "admin"}'
```

### Example 3: Multi-dimensional Array

**Input file (`readme.md`):**
```markdown
# API Documentation
...
```

**Command:**
```bash
python -m yaml_setter readme.md docs.yaml "sections[0][2].content"
```

**Result (`docs.yaml`):**
```yaml
sections:
  - - null
    - null
    - content: |
        # API Documentation
        ...
```

---

## 🛠️ Requirements

- Python 3.12+
- PyYAML

Install dependencies:
```bash
pip install pyyaml
```

---

## 📖 Advanced Usage

### Combining with Other Tools

Use in pipelines with other utilities:
```bash
# Extract, process, and store
cat source.txt | grep "pattern" > filtered.txt
python -m yaml_setter filtered.txt data.yaml "results[0].filtered"

# Batch processing
for file in logs/*.log; do
  python -m yaml_setter "$file" archive.yaml "logs[$(date +%s)].content"
done
```

### Scripting

```python
from pathlib import Path
from yaml_setter import set_yaml_value

# Process multiple files
for idx, file_path in enumerate(Path("data").glob("*.txt")):
    content = file_path.read_text()
    set_yaml_value("output.yaml", f"files[{idx}].content", content)
    set_yaml_value("output.yaml", f"files[{idx}].name", file_path.name)
```

---

## 🤝 Integration

This module works well with other `py-scripts` utilities:
- Use with `file_merger` to create composite configs
- Combine with `url_extractor` to build URL databases
- Integrate with `drive_uploader` for config management

---

## ⚠️ Notes

- String values are inserted as-is (including newlines)
- Use `|` in YAML for multi-line strings (handled automatically by PyYAML)
- Arrays are 0-indexed
- Existing values at the specified path are overwritten
- Type mismatches are resolved by replacing with correct type
