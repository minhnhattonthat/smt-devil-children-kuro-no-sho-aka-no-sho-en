-- Open the name entry (B_MAIN 0x800218D4: a0 mode 0 hero / 1 partner / 2 demon, a1 index) from the field by
-- hijacking the CPU at CALL_FRAME, let the route press buttons, then log the stored names at SAVE_ADDR.
-- Needs a route that ends in the field first (tools/routes/load_save.txt) plus the button presses to test.
local FN = NAMEENTRY_FN or 0x800218D4
local F0 = CALL_FRAME or 10000
local MODE = NAME_MODE or 0
local IDX = NAME_IDX or 0
local DUMP = DUMP_FRAME or (F0 + 900)
local ADDR = SAVE_ADDR or 0x800E0918
L.on_frame(function(n)
  if n == F0 then
    local r = PCSX.getRegisters()
    r.GPR.n.ra = r.pc
    r.GPR.n.a0 = MODE
    r.GPR.n.a1 = IDX
    r.pc = FN
  elseif n == DUMP then
    local m = PCSX.getMemPtr()
    local s = {}
    for j = 0, 18 do
      local o = ADDR - 0x80000000 + j * 2
      s[#s + 1] = string.format("%04X", m[o] + m[o + 1] * 256)
    end
    L.log("saved: " .. table.concat(s, " "))
    L.shot("after")
    L.finish(0)
  end
end)
