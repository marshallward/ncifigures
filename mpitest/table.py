import yaml

# Intel timings
with open('intel_timings.yaml') as timings_file:
    timings = yaml.load(timings_file)

intel_runtimes = []
for expt in timings:
    for run in timings[expt]:
        npes = timings[expt][run]['npes']
        time = timings[expt][run]['runtimes']['loop']
        intel_runtimes.append((npes, time))

with open('ompi_timings.yaml', 'r') as timings_file:
    timings = yaml.load(timings_file)

# OpenMPI timings
ompi_runtimes = []
for expt in timings:
    for run in timings[expt]:
        npes = timings[expt][run]['npes']
        time = timings[expt][run]['runtimes']['loop']
        ompi_runtimes.append((npes, time))

# Make the table
with open('out.txt', 'w') as tfile:
    for npes in (120, 240, 480, 960, 1920, 3840, 7680):
        print(npes, file=tfile)

        itimes = sorted([t[1] for t in intel_runtimes if t[0] == npes])
        otimes = sorted([t[1] for t in ompi_runtimes if t[0] == npes])

        print('+--------+--------+', file=tfile)
        for it, ot in zip(itimes, otimes):
            print('| {:6.1f} | {:6.1f} |'.format(it, ot), file=tfile)
        print('+--------+--------+', file=tfile)


# New table
npes = (120, 240, 480, 960, 1920, 3840, 7680)

itimes, otimes = {}, {}
for pe in npes:
    itimes[pe] = sorted([t[1] for t in intel_runtimes if t[0] == pe])
    otimes[pe] = sorted([t[1] for t in ompi_runtimes if t[0] == pe])

print('+-----------------' * len(npes) + '+')
print(''.join(['|      {:4d}       '.format(pe) for pe in npes]) + '|')
print('+--------+--------' * len(npes) + '+')
print('| Intel  | OMPI   ' * len(npes) + '|')
print('+--------+--------' * len(npes) + '+')

nmax = max(len(itimes[pe]) for pe in itimes)
for i in range(nmax):
    t_fmt = []
    for pe in npes:
        try:
            it = '{:6.1f}'.format(itimes[pe][i])
        except IndexError:
            it = ' '*6
        try:
            ot = '{:6.1f}'.format(otimes[pe][i])
        except IndexError:
            ot = ' '*6

        t_fmt.append((it, ot))

    print(''.join(['| {} | {} '.format(it, ot) for (it, ot) in t_fmt]) + '|')

print('+--------+--------' * len(npes) + '+')
