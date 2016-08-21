import yaml

# Serial timings
with open('ompi_timings.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

serial_runtimes = []
for expt in timings:
    for run in timings[expt]:
        npes = timings[expt][run]['npes']
        if npes == 960:
            time = timings[expt][run]['runtimes']['loop']
            serial_runtimes.append(time)

# Concurrent timings
with open('cc_timings.yaml') as timings_file:
    timings = yaml.load(timings_file)

runtimes = []
for expt in timings:
    for run in timings[expt]:
        npes = timings[expt][run]['ice_npes']
        time = timings[expt][run]['runtimes']['loop']
        runtimes.append((npes, time))

# Make the table
with open('out.txt', 'w') as tfile:
    print('serial', file=tfile)
    for t in serial_runtimes:
        print(t, file=tfile)

    print('------', file=tfile)

    ice_npes = set(r[0] for r in runtimes)
    for npes in sorted(ice_npes):
        print(npes, file=tfile)

        times = sorted([t[1] for t in runtimes if t[0] == npes])
        for t in times:
            print(t, file=tfile)

        print('------', file=tfile)
