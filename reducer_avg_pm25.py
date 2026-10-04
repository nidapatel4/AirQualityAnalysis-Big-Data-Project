import sys

current_station = None
total = 0.0
count = 0

for line in sys.stdin:
    try:
        line = line.strip()

        if not line:
            continue

        parts = line.split('\t')

        if len(parts) != 2:
            print(f"Skipping malformed line: {line}", file=sys.stderr)
            continue

        station, val = parts

        try:
            val = float(val)
        except ValueError:
            print(f"Skipping invalid value: {val}", file=sys.stderr)
            continue

        if station == current_station:
            total += val
            count += 1
        else:
            if current_station is not None and count > 0:
                print(f"{current_station}\t{total / count:.2f}")

            current_station = station
            total = val
            count = 1

    except Exception as e:
        print(f"Reducer error: {e}", file=sys.stderr)

if current_station is not None and count > 0:
    print(f"{current_station}\t{total / count:.2f}")