-- CPU hijack helper (PCSX-Redux): H.call(fn, a0..a3) runs a game function from wherever the game is, even a blocking one
-- (vsync callbacks keep firing, so scripts can press keys and shoot while it runs). The registers are saved and put
-- back when the function returns to a spin loop in free RAM; H.done() is true once that happened.
-- Load before scene scripts: --script tools/debug/hijack.lua
H = { active = false, count = 0 }
local SPIN = 0x8014F000
local saved
local function spin_word() return 0x08000000 + ((SPIN >> 2) & 0x3FFFFFF) end -- j SPIN (self loop); the delay slot is a nop

function H.call(fn, a0, a1, a2, a3)
  assert(not H.active, 'hijack already running')
  local m = PCSX.getMemPtr()
  local o, w = SPIN - 0x80000000, spin_word()
  for i = 0, 3 do m[o + i] = (w >> (8 * i)) & 0xFF; m[o + 4 + i] = 0 end
  local r = PCSX.getRegisters()
  saved = { pc = r.pc, r = {} }
  for i = 0, 31 do saved.r[i] = r.GPR.r[i] end
  r.GPR.n.ra = SPIN
  r.GPR.n.a0, r.GPR.n.a1, r.GPR.n.a2, r.GPR.n.a3 = a0 or 0, a1 or 0, a2 or 0, a3 or 0
  r.pc = fn
  H.active = true
end

function H.done() return not H.active end

L.on_frame(function()
  if H.active then
    local r = PCSX.getRegisters()
    if r.pc == SPIN or r.pc == SPIN + 4 then
      for i = 1, 31 do r.GPR.r[i] = saved.r[i] end
      r.pc = saved.pc
      H.active = false
      H.count = H.count + 1
    end
  end
end)
