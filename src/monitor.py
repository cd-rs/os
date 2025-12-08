import sys, os, time, webbrowser

fname = sys.argv[1] 

last = os.stat(fname).st_mtime

print("Monitoring " + fname)

while True:
    time.sleep(1)
    curr = os.stat(fname).st_mtime
    if curr != last:
        os.system("quarto render " + fname)
        last = curr
        print(last)
