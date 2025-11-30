# Assignment 4 - Market Research Tool

## Setup

I assume you have Python >=3.9.6 and pip installed.

```bash
git clone https://github.com/derrick-dacosta/a4-market-research-demo.git
```
```bash
cd a4-market-research-demo
```

```bash
pip3 install -r requirements.txt
touch .env
```

Add your API keys to `.env`:
- `ANTHROPIC_API_KEY` - from https://console.anthropic.com
- `TAVILY_API_KEY` - from https://tavily.com

## Run

```bash
python3 market_research.py
```

## Sample Questions

```bash
> What is the latest news about Comcast's market position?
```

#### Follow up Question
```bash
> Is their P/E ratio typical compared to other companies in the industry?
```
