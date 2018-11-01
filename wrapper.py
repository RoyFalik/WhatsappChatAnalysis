import sys
import analyze
import importlib

part1Cache = None
if __name__ == "__main__":
    while True:
        if not part1Cache:
            part1Cache = analyze.parse(sys.argv[1])
        analyze.analyze(part1Cache)
        print("Press enter to re-run the script, CTRL-C to exit")
        sys.stdin.readline()
        importlib.reload(analyze)
