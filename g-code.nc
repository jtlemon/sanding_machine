g56
f9000.0
g18 g21 (workplane selection)
g0x-35.0z26.25
m72(extend)
g4p0.75(delay for sander to extend)
m64m3s130(turn on sander and set pressure)
g4p0.75(delay for sander to start)

g1z313.47499999999997
g1x-571.425
g1z26.25
g1x-35.0
g1x-41.5z50.25
g1z289.47499999999997
g1x-564.925
g1z50.25
g1x-41.5
m73
m65s1000
g4p3(delay for retraction)
m5(cancel pressure control)

g56 (set wco for sander)
f9000.0(set feed speed)
g18 g21(work-plane xz and mm)
g0x-130.5z118.0(ramp in)
m72(extend)
g4p0.75(delay for sander to extend)
m64m3s130(turn on sander and set pressure)
g4p0.75(delay for sander to start)

g3x-128.5z116.0r2.0(starting)
g1x-477.9(2)
g1z223.7(3)
g1x-128.5(4)
g1z116.0(1)
g1x-477.9(2)
g1z223.7(3)
g1x-128.5(4)
g1z153.7(1-1)
g1x-427.4(2-1)
g1z186.0(3-1)
g1x-229.6(4-1)
m73
m65s1000
g4p3(delay for retraction)
m5(cancel pressure control)

m5(deactivate vacuum)
g54(reset wco)
g0x-900z0(go to park position)
