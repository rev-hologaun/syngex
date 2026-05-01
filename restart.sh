#!/bin/bash
# Kill all existing instances
ps aux | grep "python3 main.py" | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null
ps aux | grep "streamlit" | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null
sleep 2

# Clear bytecode cache
cd /home/hologaun/projects/syngex
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Launch all 10 instances
cd /home/hologaun/projects/syngex
python3 main.py --port 8200 tsla dashboard &
python3 main.py --port 8201 tsll dashboard &
python3 main.py --port 8202 intc dashboard &
python3 main.py --port 8203 amzn dashboard &
python3 main.py --port 8204 nvda dashboard &
python3 main.py --port 8205 meta dashboard &
python3 main.py --port 8206 pltr dashboard &
python3 main.py --port 8207 sofi dashboard &
python3 main.py --port 8208 spy dashboard &
python3 main.py --port 8209 qqq dashboard &

echo "All 10 instances started"
sleep 8
ps aux | grep "python3 main.py" | grep -v grep | wc -l
