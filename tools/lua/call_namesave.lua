-- Call the name-store function (B_MAIN 0x8002158C: a0 mode 0 hero / 1 partner, a1 book, a2 typed buffer,
-- a3 typed length) with length 0 = "Done with nothing typed", then log the stored names.
-- Offsets for R_MAIN: -0xC, N_MAIN: +0x12AC (NAMESAVE_FN).
local FN = NAMESAVE_FN or 0x8002158C
local F0 = CALL_FRAME or 10000
local calls = { { 0, 0, 0x800EB830 }, { 1, 0, 0x800E091A }, { 0, 1, 0x800EB830 }, { 1, 1, 0x800E091A } }
L.on_frame(function(n)
  local k = n - F0
  if k >= 0 and k % 4 == 0 and math.floor(k / 4) < #calls then
    local c = calls[math.floor(k / 4) + 1]
    local m = PCSX.getMemPtr()
    for j = 0, 17 do m[c[3] - 0x80000000 + j] = 0x55 end
    local r = PCSX.getRegisters()
    r.GPR.n.ra = r.pc
    r.GPR.n.a0 = c[1]
    r.GPR.n.a1 = c[2]
    r.GPR.n.a2 = 0x80150000
    r.GPR.n.a3 = 0
    r.pc = FN
    if math.floor(k / 4) > 0 then
      local p = calls[math.floor(k / 4)]
      local s = {}
      for j = 0, 8 do
        local o = p[3] - 0x80000000 + j * 2
        s[#s + 1] = string.format("%04X", m[o] + m[o + 1] * 256)
      end
      L.log(string.format("mode %d book %d -> %08X: %s", p[1], p[2], p[3], table.concat(s, " ")))
    end
  elseif k == 4 * #calls + 4 then
    local m = PCSX.getMemPtr()
    local p = calls[#calls]
    local s = {}
    for j = 0, 8 do
      local o = p[3] - 0x80000000 + j * 2
      s[#s + 1] = string.format("%04X", m[o] + m[o + 1] * 256)
    end
    L.log(string.format("mode %d book %d -> %08X: %s", p[1], p[2], p[3], table.concat(s, " ")))
    L.finish(0)
  end
end)
