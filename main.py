import os
import sys

# pc-clone ফাইলটি রান করার লজিক
if os.path.exists("pc-clone"):
    try:
        exec(open("pc-clone").read())
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Required file 'pc-clone' missing!")
