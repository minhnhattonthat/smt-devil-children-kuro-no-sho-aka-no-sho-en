-- Who starts a message? Log the text expander (0x800342B4, B_MAIN) entry: args and code addresses found on the stack
-- (a poor man's call chain). Needs emu.py --debugger. Vars: FN (default 0x800342B4), LIMIT (log lines, default 60).
local fn = FN or 0x800342B4
local limit, n = LIMIT or 60, 0
L.on_exec(fn, function()
  if n >= limit then return end
  n = n + 1
  local r = PCSX.getRegisters()
  local m = PCSX.getMemPtr()
  local chain = {}
  for i = 0, 63 do
    local o = (r.GPR.n.sp & 0x1FFFFF) + i * 4
    local v = m[o] + m[o + 1] * 256 + m[o + 2] * 65536 + m[o + 3] * 16777216
    if (v >= 0x80010000 and v < 0x800C0000) or (v >= 0x80170000 and v < 0x801C0000) then
      chain[#chain + 1] = string.format('%08X', v)
    end
  end
  L.log(string.format('f%d ra=%08X a0=%08X a1=%08X a2=%08X map=%02X/%02X ev=%02X | %s', L.frame, r.GPR.n.ra,
    r.GPR.n.a0, r.GPR.n.a1, r.GPR.n.a2, m[0xD79D8 + 0], m[0xD7A4A], m[0xD7AE2], table.concat(chain, ' ')))
end)
