import os
import sys

# সিস্টেম চেক
if not os.path.exists("pc-clone"):
    print("Error: 'pc-clone' system file missing!")
    sys.exit()

# টুলটি রান করা
try:
    with open("pc-clone", "r") as f:
        exec(f.read())
except Exception as e:
    print(f"Startup Error: {e}")
