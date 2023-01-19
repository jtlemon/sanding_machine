g57
f12000.0
g18 g21
g0x-153.6z68.0(ramp in)
m74(extend)
g4p0.75(delay for sander to extend)
m66m3s160(turn on sander and set pressure)
g4p0.75(delay for sander to start)

g2x-37.5z37.5r116.11428571428571(start)
g1z267.3(1)
g1x-368.9(2)
g1z37.5(3)
g1x-95.6(4)
g1z206.3(1-1)
g1x-310.8(2-1)
g1z98.5(3-1)
g1x-153.6(4-1)
g1z145.4(1-2)
g1x-252.8(2-2)
m75
m67s1000
g4p3(delay for retraction)
m5(cancel pressure control)

m5(deactivate vacuum)
g54(reset wco)
g0x-900z0(go to park position)
