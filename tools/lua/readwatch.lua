-- Log PCs that read the watched RAM range (needs emu.py --debugger). Set WATCH_ADDR / WATCH_LEN in a prepended line
-- or edit below. Logs at most 400 hits as "frame pc ra a0 a1 addr".
local WA = WATCH_ADDR or 0x801AB6D6
local WL = WATCH_LEN or 0x20
local hits, seen = 0, {}
local bp = PCSX.addBreakpoint(WA, "Read", WL, "readwatch", L.safe(function(address, width, cause)
  local r = PCSX.getRegisters()
  local pc = r.pc
  local key = tostring(pc)
  if hits < 400 and (seen[key] or 0) < 8 then
    seen[key] = (seen[key] or 0) + 1
    hits = hits + 1
    L.log(string.format("%d pc=%08X ra=%08X a0=%08X a1=%08X s0=%08X s1=%08X addr=%08X", L.frame, pc,
      r.GPR.n.ra, r.GPR.n.a0, r.GPR.n.a1, r.GPR.n.s0, r.GPR.n.s1, address))
  end
  return false
end))
