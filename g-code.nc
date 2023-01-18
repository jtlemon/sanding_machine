g55 (set wco for sander)
f9000.0(set feed speed)
g18 g21(work-plane xz and mm)
g0x-122.0z109.5(ramp in)
m70(extend)
g4p0.75(delay for sander to extend)
m62m3s200(turn on sander and set pressure)
g4p0.75(delay for sander to start)

g3x-121.0z108.5r1.0(starting)
g1x--91.0(2)
g1z-92.5(3)
g1x-121.0(4)
g1z108.5(1)
g1x--91.0(2)
g1z-92.5(3)
g1x-121.0(4)
m71
m63s1000
g4p3(delay for retraction)
m5(cancel pressure control)

g56 (set wco for sander)
f9000.0(set feed speed)
g18 g21(work-plane xz and mm)
g0x-122.0z109.5(ramp in)
m72(extend)
g4p0.75(delay for sander to extend)
m64m3s200(turn on sander and set pressure)
g4p0.75(delay for sander to start)

g3x-121.0z108.5r1.0(starting)
g1x--91.0(2)
g1z-92.5(3)
g1x-121.0(4)
m73
m65s1000
g4p3(delay for retraction)
m5(cancel pressure control)

g57
f9000.0
g18 g21 (workplane selection)
g0x-35.0z35.0
m74(extend)
g4p0.75(delay for sander to extend)
m66m3s200(turn on sander and set pressure)
g4p0.75(delay for sander to start)

g1z-19.0
g1x--5.0
g1z35.0
g1x-35.0
m75
m67s1000
g4p3(delay for retraction)
m5(cancel pressure control)

g58
f9000.0
g18 g21 (workplane selection)
g0x-35.0z35.0
m78(extend)
g4p0.75(delay for sander to extend)
m68m3s200(turn on sander and set pressure)
g4p0.75(delay for sander to start)

g1z-19.0
g1x--5.0
g1z35.0
g1x-35.0
m79
m69s1000
g4p3(delay for retraction)
m5(cancel pressure control)

m5(deactivate vacuum)
g54(reset wco)
g0x-900z0(go to park position)
