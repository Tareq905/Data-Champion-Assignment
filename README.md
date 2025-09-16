# AI Exam Revision Agent

An advanced CLI-based tool for generating **personalized revision plans** and **quiz questions** for any subject. This agent can create structured study schedules over a set number of days, optionally leveraging OpenAI's GPT models to generate adaptive plans.

---

## Features

* Parse flexible input formats like:
  `Subject; topics: A,B,C; days: 10; style: active`
* Generate **daily study schedules** with priority intervals (SM2-based).
* Create **sample quiz questions** for each topic.
* Save and load **progress logs** in JSON format.
* Integrates with OpenAI GPT models if API key is provided, for AI-generated schedules.
* Fully **CLI-driven**, easy to integrate into scripts or automation.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Tareq905/Data-Champion-Assignment.git
cd Data-Champion-Assignment
```

2. (Optional) Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies (OpenAI is optional):

```bash
pip install openai
```

4. Set your OpenAI API key (optional):

```bash
export OPENAI_API_KEY="your_api_key_here"  # Linux/Mac
setx OPENAI_API_KEY "your_api_key_here"    # Windows
```

---

## Usage

Run the CLI:

```bash
python main.py --input "Subject; topics: A,B,C; days:10; style: active" --save-progress progress.json
```

### CLI Options

* `--input` or `-i`: Input string describing the study plan.
* `--progress` or `-p`: Path to an existing progress JSON file.
* `--save-progress` or `-s`: Path to save progress JSON file.

Example:

```bash
python main.py -i "Physics; topics: Mechanics, Optics; days:7; style: active" -s progress.json
```

---

## Output

The program prints a **personalized revision plan** with sample quiz questions in a table format:

```
📘 Personalized Revision Plan

| Day | Topic | Sample Quiz Questions |
|-----|-------|------------------------|
| 1   | Mechanics | What is the core concept of Mechanics? || Explain a key example/problem for Mechanics. || List 3 important definitions in Mechanics. |
| 2   | Optics    | What is the core concept of Optics? || Explain a key example/problem for Optics. || List 3 important definitions in Optics. |
...
```

Progress can be saved to a JSON file and updated after each session.

---

## License

MIT License
