-- Log the first PCs executed inside any range of XR = {{lo, hi}, ...} (--var): proves "dead" code really never runs.
-- Exec breakpoints make emulation slow (needs emu.py --debugger); use it on short scenes.
local hits = 0
for _, r in ipairs(XR) do
  PCSX.addBreakpoint(r[1], 'Exec', r[2] - r[1], 'execwatch', L.safe(function(address)
    if hits < 40 then
      hits = hits + 1
      L.log(string.format('EXEC frame %d range %08X pc=%08X ra=%08X', L.frame, r[1], address, PCSX.getRegisters().GPR.n.ra))
    end
    return false
  end))
end
