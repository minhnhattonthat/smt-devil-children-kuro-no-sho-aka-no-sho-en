-- Debug warp: from a field savestate, call a game function by hijacking the CPU (it returns to where the CPU was).
--   --var FN=0x800523A8 --var A0=1 [--var A1=.. A2=.. A3=..] [--var AT=30] [--var POKE='{[0x800D7AE3]=1}']
-- POKE: table addr -> byte written at frame AT-1 (flags/ids the function reads).
local at = AT or 30
L.on_frame(function(n)
  if n == at - 1 and POKE then
    local m = PCSX.getMemPtr()
    for a, v in pairs(POKE) do m[a - 0x80000000] = v end
  elseif n == at then
    local r = PCSX.getRegisters()
    r.GPR.n.ra = r.pc
    r.GPR.n.a0, r.GPR.n.a1, r.GPR.n.a2, r.GPR.n.a3 = A0 or 0, A1 or 0, A2 or 0, A3 or 0
    r.pc = FN
    L.log(string.format('warp: call %08X(%X,%X) from pc %08X', FN, A0 or 0, A1 or 0, r.pc))
  end
end)
