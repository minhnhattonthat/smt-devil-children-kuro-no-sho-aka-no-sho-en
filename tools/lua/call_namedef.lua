-- Call the default-name function (B_MAIN 0x800212A4: a0 mode, a1 index, a2 buffer) by hijacking the CPU at
-- frame CALL_FRAME (the field, after tools/routes/load_save.txt), then log each buffer as halfwords.
-- Modes: 0 hero label, 1 partner label, 4 demon record name of party slot a1.
local FN = NAMEDEF_FN or 0x800212A4
local F0 = CALL_FRAME or 10000
local BUF = 0x80150000
local calls = { { 0, 0 }, { 1, 0 }, { 4, 0 }, { 0, 1 }, { 1, 1 } }
L.on_frame(function(n)
  local k = n - F0
  if k >= 0 and k % 2 == 0 and math.floor(k / 2) < #calls then
    local c = calls[math.floor(k / 2) + 1]
    local r = PCSX.getRegisters()
    r.GPR.n.ra = r.pc
    r.GPR.n.a0 = c[1]
    r.GPR.n.a1 = c[2]
    r.GPR.n.a2 = BUF + (math.floor(k / 2)) * 0x40
    r.pc = FN
  elseif k == 2 * #calls + 2 then
    local m = PCSX.getMemPtr()
    for i = 0, #calls - 1 do
      local s = {}
      for j = 0, 17 do
        local o = (BUF + i * 0x40 + j * 2) - 0x80000000
        s[#s + 1] = string.format("%04X", m[o] + m[o + 1] * 256)
      end
      L.log(string.format("call %d mode=%d idx=%d: %s", i, calls[i + 1][1], calls[i + 1][2], table.concat(s, " ")))
    end
    L.finish(0)
  end
end)
